import os
import os.path
import scipy.io as sio
import numpy as np
import struct


dataset_dir = '/home/x/DB/MSRA HandPoseDataset/cvpr15_MSRAHandGestureDB/'
save_dir = '/home/x/Codes/3D_Point_Projective_D_TSDF/results'

subject_names = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
gesture_names = ['1', '2', '3', '4', '5', '6', '7', '8',
                 '9', 'I', 'IP', 'L', 'MP', 'RP', 'T', 'TIP', 'Y']


class Read_MSRA(object):

    def __init__(self):
        self.MSRA_valid = self.read_valid()
        # self.read_all()

    def read_valid(self):
        raw = sio.loadmat('./msra_valid.mat')
        data = raw['msra_valid']
        return data

    def read_all(self):

        for sub in range(len(subject_names)):

            try:
                os.mkdir(save_dir)
                os.mkdir(os.path.join(save_dir, subject_names[sub]))
            except:
                print('1st directory already exist!')
            else:
                print('create directory %s' % subject_names[sub])

            for ges in range(len(gesture_names)):

                ges_dir = os.path.join(
                    dataset_dir, subject_names[sub], gesture_names[ges])

                save_ges_dir = os.path.join(
                    save_dir, subject_names[sub], gesture_names[ges])

                # read ground truth
                ground_truth = self.read_ground_truth(ges_dir, save_ges_dir)
                # create save files
                try:
                    os.mkdir(save_ges_dir)
                except:
                    print('2nd directory already exist!')
                else:
                    print('create directory %s' %
                          subject_names[sub]+'/'+gesture_names[ges])

                [jnt_xyz, hand_points] = self.read_depth_bin(
                    ges_dir, save_ges_dir, sub, ges, ground_truth)
                self.save_mat(save_ges_dir, jnt_xyz, hand_points)

    def read_ground_truth(self, ges_dir, save_ges_dir):

        joint_txt = os.path.join(ges_dir, 'joint.txt')

        with open(joint_txt, 'r') as f:
            frame_num = int(f.readline())
        # 跳过第一行，不然会显示numpy 列对不上，第一行只有 frame_num 一个数值，比下面的少
        truth_data = np.loadtxt(joint_txt, skiprows=1)
        ground_truth = truth_data.reshape(frame_num, 21, 3)
        # 因为深度图z是正的，但是label里面z却是负数
        ground_truth[:, :, 2] = -ground_truth[:, :, 2]

        return ground_truth

    def read_depth_bin(self, ges_dir, save_ges_dir, sub, ges, ground_truth):

        num = 0
        for i in os.listdir(ges_dir):
            if os.path.splitext(i)[1] == '.bin':
                num += 1

        valid = self.MSRA_valid[sub, ges]
        for frm in range(num):
            if not valid[frm]:
                continue
            hand_points = self.read_conv_bin(ges_dir, frm, save_ges_dir)
            jnt_xyz = np.squeeze(ground_truth[frm, :, :])

        return jnt_xyz, hand_points

        # read binary files
    def read_conv_bin(self, ges_dir, frm, save_ges_dir):

        with open(ges_dir + '/' + str('%06d' % frm) + '_depth.bin', 'rb') as f:
            img_width = struct.unpack('I', f.read(4))[0]
            img_height = struct.unpack('I', f.read(4))[0]

            bb_left = struct.unpack('I', f.read(4))[0]
            bb_top = struct.unpack('I', f.read(4))[0]
            bb_right = struct.unpack('I', f.read(4))[0]
            bb_bottom = struct.unpack('I', f.read(4))[0]
            bb_width = bb_right - bb_left
            bb_height = bb_bottom - bb_top
            valid_pixel_num = bb_width * bb_height

            hand_depth = struct.unpack(
                'f'*valid_pixel_num, f.read(4*valid_pixel_num))

        hand_depth = np.array(hand_depth, dtype=np.float32)
        hand_depth = hand_depth.reshape(bb_width, bb_height)
        hand_depth = hand_depth.transpose()

        np.savetxt(save_ges_dir+'/depth.txt', hand_depth)

        fFocal_msra = 241.42
        hand_3d = np.zeros((valid_pixel_num, 3))
        for ii in range(bb_height):
            for jj in range(bb_width):
                '''
                0 < ii < bb_height - 1   
                0 < jj < bb_weight - 1
                0 < idx < h * w -1
                '''
                idx = jj * bb_height + ii
                hand_3d[idx, 0] = -(img_width/2 - (jj + bb_left)
                                    ) * hand_depth[ii, jj]/fFocal_msra
                hand_3d[idx, 1] = -(img_height/2 - (ii + bb_top)
                                    ) * hand_depth[ii, jj] / fFocal_msra
                hand_3d[idx, 2] = hand_depth[ii, jj]
        np.savetxt(save_ges_dir+'/depth_3d.txt', hand_3d)

        valid_idx = []

        for num in range(valid_pixel_num):
            if any(hand_3d[num, :]):
                valid_idx.append(num)

        hand_points = hand_3d[valid_idx, :]

        np.savetxt(save_ges_dir+'/v_3D.txt', hand_points)

        return hand_points

    def save_mat(self, save_ges_dir, jnt_xyz, hand_points):

        sio.savemat(save_ges_dir+'/jnt_xyz.mat', {'joint': jnt_xyz})
        sio.savemat(save_ges_dir+'/hand_points.mat',
                    {'hand_points': hand_points})


if __name__ == '__main__':
    r = Read_MSRA()
    r.read_all()
