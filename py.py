for i in range(0,len(fd_name)):
    iact = int(pose_id[i])
    ifd = fd_name[i]
    fname = os.listdir(r'C:\Users\user\Desktop\연구\7. CATGCN\AI_DataSet_MP4_JSON\\' + ifd)

    for j in range(len(fname)):
        ifn = fname[j]
        if ifn.split('.')[-1] == 'json':
            # print(ifn) 
            
            ### Opening JSON file
            with open(r'C:\Users\user\Desktop\연구\7. CATGCN\AI_DataSet_MP4_JSON\\' + ifd + '/' + ifn, 'r', encoding='utf-8') as openfile:
             # Reading from json file
             json_object = json.load(openfile)
             print(json_object)
             
            # pose
            keypoints = json_object['annotations']['keypoints']
            nframe = len(keypoints)

            if nframe >= 300:
              dta = []
              ith_frame = 0
              for iframe in list(np.linspace(1, nframe, 300,dtype='int')):
                pose = list(np.array(keypoints[iframe-1])[indices])
                
                pose[0:len(pose):2] = list(np.array(pose[0:len(pose):2])/1920)
                pose[1:len(pose):2] = list(np.array(pose[1:len(pose):2])/1080)
                
                for i in range(0,len(pose)):
                  pose[i] = round(pose[i],3)

                # score
                score = []
                for i in range(0,18):
                  score.append(round(float(0.7 + rng_score*0.2),3))

                # Make a dictionary object
                skt = list()
                skt.append({"pose": pose, "score": score})
                dta.append({"frame_index": ith_frame, "skeleton": skt})
                ith_frame += 1

            else:  
              dta = []
              for iframe in range(1,nframe+1):
                pose = list(np.array(keypoints[iframe-1])[indices])
                
                pose[0:len(pose):2] = list(np.array(pose[0:len(pose):2])/1920)
                pose[1:len(pose):2] = list(np.array(pose[1:len(pose):2])/1080)
                
                for q in range(0,len(pose)):
                  pose[q] = round(pose[q],3)

                # score
                score = []
                for k in range(0,18):
                  score.append(round(float(0.7 + np.random.random(1)*0.2),3))

                # Make a dictionary object
                skt = list()
                skt.append({"pose": pose, "score": score})
                dta.append({"frame_index": iframe-1, "skeleton": skt})
                
              for iframe in range(nframe,300):
                # Make a dictionary object
                skt = list()
                #skt.append({"pose": [], "score": []})
                dta.append({"frame_index": iframe, "skeleton": skt})
                
            ### Writing JSON file
            out = {"data": dta,
                    "label": "a"+str(iact),
                    "label_index": iact}  
      
            tmpname = ifn.split('_')

            # if te.rvs(1, random_state = rng_split)[0] == 1:
            #   outfname = './data/fire_val/__a'+str(iact)+'_'+tmpname[1]+'_'+tmpname[2]+'_'+'f'+str(j)+'.json'
            # else:
            #   outfname = './data/fire_train/__a'+str(iact)+'_'+tmpname[1]+'_'+tmpname[2]+'_'+'f'+str(j)+'.json'
              
            # with open(outfname, "w", encoding="UTF-8") as outfile:
            #   json.dump(out, outfile)
              