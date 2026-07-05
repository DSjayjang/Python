# -*- coding: utf-8 -*-
"""
CATS-GCN Data Leakage 검사 스크립트

파일명 형식: a{action}_p{pose}_b{body}_pos(x,y,z)_rot(x,y,z).json
핵심 아이디어: 원본 모션 시퀀스는 (action, pose) = (a, p) 조합으로 식별된다.
b(캐릭터), pos/rot(뷰포인트)는 동일 원본에서 파생된 증강(augmentation)이므로
동일한 (a, p)가 train과 validation에 모두 존재하면 data leakage로 간주한다.

사용법:
    python check_leakage.py <train_root> <val_root>

예:
    python check_leakage.py \
      "C:\\...\\Training\\02.라벨링데이터\\TL\\AI 학습용 동영상" \
      "C:\\...\\Validation\\02.라벨링데이터\\VL\\AI 학습용 동영상"

TL/VL 아래에 클래스별 하위 폴더(1, 2, 3, ... 341)가 있다는 전제로,
train_root와 val_root는 "AI 학습용 동영상"까지의 경로를 넣으면 됩니다.
(즉 그 아래 1, 2, ..., 341 폴더가 있는 위치)
"""

import os
import re
import sys
import json
from collections import defaultdict

# 파일명 패턴: a1_p0_b0_pos(-1,3.2,-8)_rot(23,11,0).json
PATTERN = re.compile(
    r'^a(?P<action>\d+)_p(?P<pose>\d+)_b(?P<body>\d+)_'
    r'pos\((?P<pos>[^)]*)\)_rot\((?P<rot>[^)]*)\)\.json$',
    re.IGNORECASE
)


def parse_filename(fname):
    m = PATTERN.match(fname)
    if not m:
        return None
    return {
        'action': int(m.group('action')),
        'pose': int(m.group('pose')),
        'body': int(m.group('body')),
        'pos': m.group('pos'),
        'rot': m.group('rot'),
        'filename': fname,
    }


def scan_folder(root):
    """
    root 아래의 모든 하위 폴더(클래스별 1, 2, 3, ...)를 재귀적으로 순회하며
    json 파일명을 파싱한다.
    반환: dict[action] -> set of (action, pose) tuples 아님. 대신
          dict[action] -> dict[pose] -> list of full filenames
    """
    result = defaultdict(lambda: defaultdict(list))
    unparsed = []
    total_files = 0

    if not os.path.isdir(root):
        print(f"[경고] 경로가 존재하지 않습니다: {root}")
        return result, unparsed, total_files

    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if not fname.lower().endswith('.json'):
                continue
            total_files += 1
            parsed = parse_filename(fname)
            if parsed is None:
                unparsed.append(os.path.join(dirpath, fname))
                continue
            result[parsed['action']][parsed['pose']].append(fname)

    return result, unparsed, total_files


def main(train_root=None, val_root=None):
    # ------------------------------------------------------------------
    # Jupyter / IPython 사용자를 위한 경로 설정
    # 아래 두 변수에 직접 경로를 채워넣고 실행하면 됩니다.
    # (터미널에서 argument로 실행할 경우 이 값들은 무시되고 sys.argv를 사용합니다)
    # ------------------------------------------------------------------
    DEFAULT_TRAIN_ROOT = r"C:\Users\user\Desktop\연구\7. CATGCN\1. Revision\소방\056.소방대원 행동모션 3D 객체 모델링 데이터\01-1.정식개방데이터\Training\02.라벨링데이터\TL\AI 학습용 동영상"
    DEFAULT_VAL_ROOT = r"C:\Users\user\Desktop\연구\7. CATGCN\1. Revision\소방\056.소방대원 행동모션 3D 객체 모델링 데이터\01-1.정식개방데이터\Validation\02.라벨링데이터\VL\AI 학습용 동영상"

    if train_root is None or val_root is None:
        if len(sys.argv) == 3:
            train_root = sys.argv[1]
            val_root = sys.argv[2]
        else:
            train_root = DEFAULT_TRAIN_ROOT
            val_root = DEFAULT_VAL_ROOT
            print("[안내] 명령줄 인자가 없어 스크립트 내 DEFAULT 경로를 사용합니다.")
            print("       다른 경로를 쓰려면 main(train_root=r'...', val_root=r'...') 형태로 호출하세요.\n")

    print("=" * 70)
    print("Train 폴더 스캔 중...")
    train_data, train_unparsed, train_total = scan_folder(train_root)
    print(f"  총 json 파일: {train_total}개")
    print(f"  파싱 실패 파일: {len(train_unparsed)}개")
    if train_unparsed[:5]:
        print("  (예시)", train_unparsed[:5])

    print("=" * 70)
    print("Validation 폴더 스캔 중...")
    val_data, val_unparsed, val_total = scan_folder(val_root)
    print(f"  총 json 파일: {val_total}개")
    print(f"  파싱 실패 파일: {len(val_unparsed)}개")
    if val_unparsed[:5]:
        print("  (예시)", val_unparsed[:5])

    print("=" * 70)
    print("클래스(action)별 (action, pose) 조합 교집합(leakage) 검사")
    print("=" * 70)

    all_actions = sorted(set(train_data.keys()) | set(val_data.keys()))

    total_leaked_ap_pairs = 0
    total_train_ap_pairs = 0
    total_val_ap_pairs = 0
    leaked_actions = []

    detail_rows = []

    for action in all_actions:
        train_poses = set(train_data.get(action, {}).keys())
        val_poses = set(val_data.get(action, {}).keys())

        overlap = train_poses & val_poses

        total_train_ap_pairs += len(train_poses)
        total_val_ap_pairs += len(val_poses)
        total_leaked_ap_pairs += len(overlap)

        if overlap:
            leaked_actions.append(action)

        detail_rows.append({
            'action': action,
            'train_pose_count': len(train_poses),
            'val_pose_count': len(val_poses),
            'overlap_pose_count': len(overlap),
            'overlap_poses': sorted(overlap),
        })

    # 클래스 1번 상세 출력 (사용자가 준 예시 검증용)
    print("\n[클래스 a1 상세]")
    row = next((r for r in detail_rows if r['action'] == 1), None)
    if row:
        print(f"  train pose 종류 수: {row['train_pose_count']}")
        print(f"  val   pose 종류 수: {row['val_pose_count']}")
        print(f"  겹치는 pose(원본 시퀀스): {row['overlap_poses']}")
        if row['overlap_poses']:
            for p in row['overlap_poses']:
                print(f"    - p{p}:")
                print(f"        train 파일: {train_data[1][p]}")
                print(f"        val   파일: {val_data[1].get(p, [])}")

    print("\n" + "=" * 70)
    print("전체 요약")
    print("=" * 70)
    print(f"검사한 클래스(action) 수: {len(all_actions)}")
    print(f"Leakage가 발견된 클래스 수: {len(leaked_actions)} / {len(all_actions)}")
    if leaked_actions:
        print(f"  -> 해당 action 목록(최대 30개 표시): {leaked_actions[:30]}")

    total_pairs_union = total_train_ap_pairs  # 참고용
    leak_ratio = (total_leaked_ap_pairs / total_val_ap_pairs * 100) if total_val_ap_pairs else 0
    print(f"\n전체 (action,pose) 조합 수 (train): {total_train_ap_pairs}")
    print(f"전체 (action,pose) 조합 수 (val)  : {total_val_ap_pairs}")
    print(f"train/val 양쪽에 모두 존재하는 (action,pose) 조합 수: {total_leaked_ap_pairs}")
    print(f"-> validation 조합 중 leakage 비율: {leak_ratio:.1f}%")

    # 결과를 파일로도 저장
    out_path = os.path.join(os.getcwd(), "leakage_report.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'train_total_files': train_total,
            'val_total_files': val_total,
            'train_unparsed_count': len(train_unparsed),
            'val_unparsed_count': len(val_unparsed),
            'num_actions_checked': len(all_actions),
            'num_actions_with_leakage': len(leaked_actions),
            'leaked_actions': leaked_actions,
            'total_train_ap_pairs': total_train_ap_pairs,
            'total_val_ap_pairs': total_val_ap_pairs,
            'total_leaked_ap_pairs': total_leaked_ap_pairs,
            'leak_ratio_percent': leak_ratio,
            'per_action_detail': detail_rows,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n상세 리포트 저장됨: {out_path}")


if __name__ == '__main__':
    main()

# ------------------------------------------------------------------
# Jupyter Notebook / IPython에서 사용하는 방법:
#
#   %run check_leakage.py   (인자 없이 실행 시 -> 스크립트 안의 DEFAULT 경로 사용)
#
# 또는 직접 경로를 지정하고 싶다면 노트북 셀에서:
#
#   import check_leakage
#   check_leakage.main(
#       train_root=r"C:\...\Training\02.라벨링데이터\TL\AI 학습용 동영상",
#       val_root=r"C:\...\Validation\02.라벨링데이터\VL\AI 학습용 동영상"
#   )
# ------------------------------------------------------------------
