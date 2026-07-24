# -*- coding: utf-8 -*-
"""
CATS-GCN Grouped Split 생성 스크립트 (Leakage 방지)

배경:
    파일명 형식: a{action}_p{character}_b{background}_pos(...)_rot(...).json
    클래스당 45개 = 캐릭터(p) 3종 x 배경(b) 3종 x 다각도(rot) 5종
    실제 배포본에는 정제 과정에서 일부 누락되어 클래스당 41개 내외로 존재.

    기존 AI-Hub 공식/배포 split은 (action, p, b, rot) 개별 샘플 단위로
    Train/Validation을 나누어, 동일한 (action, p, b) 조합의 다른 rot(카메라 각도)
    variant가 train과 val에 걸쳐 존재하는 data leakage가 발생함 (검증 완료:
    val (action,pose) 조합의 100%가 train에도 존재).

이 스크립트가 하는 일:
    1. 기존 Train + Validation 폴더의 모든 json 파일을 하나의 pool로 합친다.
    2. 각 action(클래스)마다 파일들을 (p, b) 조합 단위로 그룹화한다.
       -> 클래스당 최대 9개 그룹 (p 3종 x b 3종), 그룹당 최대 5개 파일(rot 5종).
    3. 클래스마다 그룹 전체를 통째로 train 또는 test 중 한쪽에만 배정한다.
       (동일 그룹 안의 rot variant들이 절대 양쪽에 나뉘지 않도록 보장)
       기본 규칙: 그룹이 9개면 7 train : 2 test.
                  그룹 수가 9개가 아니면 가능한 한 8:2에 가까운 정수 조합 사용.
    4. 그룹 배정은 무작위이되 seed 고정으로 재현 가능하게 한다.
    5. 결과를 new_split_manifest.csv / .json 으로 저장한다.
       (실제 파일 복사는 하지 않음 -- pkl 재구성은 이 매니페스트를 참고해서 진행)

사용법 (터미널):
    python make_grouped_split.py <train_root> <val_root> [--seed 42]

Jupyter/IPython:
    import make_grouped_split as mgs
    mgs.main(train_root=r"...", val_root=r"...", seed=42)
"""

import os
import re
import sys
import json
import csv
import random
from collections import defaultdict

PATTERN = re.compile(
    r'^a(?P<action>\d+)_p(?P<character>\d+)_b(?P<background>\d+)_'
    r'pos\((?P<pos>[^)]*)\)_rot\((?P<rot>[^)]*)\)\.json$',
    re.IGNORECASE
)


def parse_filename(fname):
    m = PATTERN.match(fname)
    if not m:
        return None
    return {
        'action': int(m.group('action')),
        'character': int(m.group('character')),
        'background': int(m.group('background')),
        'pos': m.group('pos'),
        'rot': m.group('rot'),
        'filename': fname,
    }


def scan_folder(root, origin_label):
    """
    root 아래를 재귀 탐색하여 json 파일을 찾고 파싱한다.
    origin_label: 'train' 또는 'val' -- 원래 어느 폴더에서 왔는지 기록용
    반환: list of dict (parsed + filepath + origin)
    """
    records = []
    unparsed = []

    if not os.path.isdir(root):
        print(f"[경고] 경로가 존재하지 않습니다: {root}")
        return records, unparsed

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if not fname.lower().endswith('.json'):
                continue
            parsed = parse_filename(fname)
            if parsed is None:
                unparsed.append(os.path.join(dirpath, fname))
                continue
            parsed['filepath'] = os.path.join(dirpath, fname)
            parsed['origin'] = origin_label
            records.append(parsed)

    return records, unparsed


def choose_test_group_count(num_groups):
    """
    클래스별 (p,b) 그룹 총 개수에 따라 8:2에 가장 가까운 test 그룹 개수를 결정.
    그룹 크기가 정수이므로 정확한 8:2는 대부분 불가능 -> 가장 가까운 정수 선택.
    """
    if num_groups <= 1:
        return 0
    best_test_n = 1
    best_diff = float('inf')
    for test_n in range(1, num_groups):
        ratio = test_n / num_groups
        diff = abs(ratio - 0.2)
        if diff < best_diff:
            best_diff = diff
            best_test_n = test_n
    return best_test_n


def main(train_root=None, val_root=None, seed=42):
    DEFAULT_TRAIN_ROOT = r"C:\Users\user\Desktop\연구\7. CATGCN\1. Revision\소방\056.소방대원 행동모션 3D 객체 모델링 데이터\01-1.정식개방데이터\Training\02.라벨링데이터\TL\AI 학습용 동영상"
    DEFAULT_VAL_ROOT = r"C:\Users\user\Desktop\연구\7. CATGCN\1. Revision\소방\056.소방대원 행동모션 3D 객체 모델링 데이터\01-1.정식개방데이터\Validation\02.라벨링데이터\VL\AI 학습용 동영상"

    if train_root is None or val_root is None:
        if len(sys.argv) >= 3:
            train_root = sys.argv[1]
            val_root = sys.argv[2]
        else:
            train_root = DEFAULT_TRAIN_ROOT
            val_root = DEFAULT_VAL_ROOT
            print("[안내] 인자가 없어 스크립트 내 DEFAULT 경로를 사용합니다.\n")

    random.seed(seed)

    print("=" * 70)
    print("Train + Validation 폴더 스캔 중 (전체를 하나의 pool로 합침)...")
    train_records, train_unparsed = scan_folder(train_root, 'train')
    val_records, val_unparsed = scan_folder(val_root, 'val')
    all_records = train_records + val_records

    print(f"  기존 train 파일: {len(train_records)}개, 파싱 실패: {len(train_unparsed)}개")
    print(f"  기존 val   파일: {len(val_records)}개, 파싱 실패: {len(val_unparsed)}개")
    print(f"  합계 pool: {len(all_records)}개")

    # action -> (character, background) -> list of records
    grouped = defaultdict(lambda: defaultdict(list))
    for rec in all_records:
        key = (rec['character'], rec['background'])
        grouped[rec['action']][key].append(rec)

    new_split = []  # 최종 결과 담을 리스트: dict(filename, action, character, background, rot, new_split, old_origin)

    summary_rows = []
    total_train_files = 0
    total_test_files = 0

    for action in sorted(grouped.keys()):
        pb_groups = grouped[action]  # dict: (p,b) -> list of records
        group_keys = list(pb_groups.keys())
        random.shuffle(group_keys)  # 그룹 배정 순서를 무작위화 (seed 고정으로 재현 가능)

        num_groups = len(group_keys)
        test_group_n = choose_test_group_count(num_groups)

        test_groups = set(group_keys[:test_group_n])
        train_groups = set(group_keys[test_group_n:])

        class_train_count = 0
        class_test_count = 0

        for key in group_keys:
            split_label = 'test' if key in test_groups else 'train'
            for rec in pb_groups[key]:
                new_split.append({
                    'filename': rec['filename'],
                    'filepath': rec['filepath'],
                    'action': action,
                    'character': rec['character'],
                    'background': rec['background'],
                    'rot': rec['rot'],
                    'old_origin': rec['origin'],
                    'new_split': split_label,
                })
                if split_label == 'train':
                    class_train_count += 1
                else:
                    class_test_count += 1

        total_train_files += class_train_count
        total_test_files += class_test_count

        summary_rows.append({
            'action': action,
            'num_groups': num_groups,
            'test_group_n': test_group_n,
            'train_files': class_train_count,
            'test_files': class_test_count,
            'ratio_test_pct': round(100 * class_test_count / (class_train_count + class_test_count), 1)
                              if (class_train_count + class_test_count) > 0 else 0.0,
        })

    print("\n" + "=" * 70)
    print("그룹 단위 재분할 결과 요약")
    print("=" * 70)
    total_files = total_train_files + total_test_files
    print(f"전체 파일 수: {total_files}")
    print(f"새 train: {total_train_files}개 ({100*total_train_files/total_files:.1f}%)")
    print(f"새 test : {total_test_files}개 ({100*total_test_files/total_files:.1f}%)")

    # 클래스별 비율 분포 확인 (편차 체크용)
    ratios = [r['ratio_test_pct'] for r in summary_rows]
    if ratios:
        print(f"\n클래스별 test 비율(%) - 최소: {min(ratios)}, 최대: {max(ratios)}, "
              f"평균: {sum(ratios)/len(ratios):.1f}")

    # a1 클래스 상세 출력 (검증용)
    row1 = next((r for r in summary_rows if r['action'] == 1), None)
    if row1:
        print(f"\n[클래스 a1 검증] 그룹 수: {row1['num_groups']}, "
              f"test로 배정된 그룹 수: {row1['test_group_n']}, "
              f"train 파일: {row1['train_files']}, test 파일: {row1['test_files']}, "
              f"test 비율: {row1['ratio_test_pct']}%")

    # -----------------------------------------------------------------
    # 결과 저장: manifest CSV (파일별 new_split 배정 결과) + summary CSV
    # -----------------------------------------------------------------
    out_dir = os.getcwd()
    manifest_path = os.path.join(out_dir, "new_split_manifest.csv")
    with open(manifest_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'filename', 'filepath', 'action', 'character', 'background',
            'rot', 'old_origin', 'new_split'
        ])
        writer.writeheader()
        for row in new_split:
            writer.writerow(row)
    print(f"\n파일별 배정 결과 저장됨: {manifest_path}")

    summary_path = os.path.join(out_dir, "new_split_summary.csv")
    with open(summary_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'action', 'num_groups', 'test_group_n', 'train_files',
            'test_files', 'ratio_test_pct'
        ])
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)
    print(f"클래스별 요약 저장됨: {summary_path}")

    # leakage 검증: 그룹 단위로 나눴으므로 (action, character, background)가
    # train/test 양쪽에 동시에 존재하면 안 됨 -> 자체 검증
    verify_map = defaultdict(set)
    for row in new_split:
        key = (row['action'], row['character'], row['background'])
        verify_map[key].add(row['new_split'])

    leaked_groups = [k for k, v in verify_map.items() if len(v) > 1]
    print(f"\n[자체 검증] 그룹이 train/test 양쪽에 걸친 경우: {len(leaked_groups)}개 "
          f"(0이어야 정상)")
    if leaked_groups:
        print(f"  -> 문제 그룹 예시: {leaked_groups[:5]}")
    else:
        print("  -> 통과: 모든 (action, character, background) 그룹이 한쪽에만 배정됨")

    return new_split, summary_rows


if __name__ == '__main__':
    main()

# ------------------------------------------------------------------
# 다음 단계:
#   new_split_manifest.csv 의 'filepath'와 'new_split' 컬럼을 이용해
#   실제 pkl(또는 학습 파이프라인의 파일 리스트)을 재구성하면 됩니다.
#   예: new_split == 'train'인 filepath들을 모아 새 train.pkl 생성,
#       new_split == 'test'인 filepath들을 모아 새 test.pkl 생성.
# ------------------------------------------------------------------
