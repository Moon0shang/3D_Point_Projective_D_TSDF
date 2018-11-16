import os
import os.path
import numpy as np
import scipy.io as sio

from MSRA_pre import Read_MSRA
from visualize_3D import visualize
from TSDF import tsdf


def initial_data():
    '''
    only need to run once!
    '''
    read_data = Read_MSRA()
    read_data.read_all()


def show_points(file_dir):

    hand_points_raw = sio.loadmat(file_dir)
    hand_points = hand_points_raw['points']

    visualize(hand_points)


def run_TSDF(file_dir):

    hand_points_raw = sio.loadmat(file_dir)
    hand_points = hand_points_raw['points']
    hand_ori = hand_points_raw['hand_ori']
    pic_info = hand_points_raw['pic_info'][0]

    tsdf_v = tsdf(hand_points, hand_ori, pic_info)

    sio.savemat('./tsdf/tsdf.mat', {'tsdf': tsdf_v})
    print('tsdf files saved')

    return tsdf_v


def show_TSDF(file_dir, d):

    tsdf_v = sio.loadmat(file_dir)
    tsdf_v = tsdf_v['tsdf']

    idx = np.where(tsdf_v[0, :, :, :] == 1)

    px = idx[0]
    py = idx[1]
    pz = idx[2]

    point_show = np.array([px, py, pz], dtype=np.float32)

    visualize(point_show)


if __name__ == '__main__':

    # initial_data()
    # select_file_dir = './results/P0/1/points000.mat'
    # show_points(select_file_dir)
    # tsdf_v = run_TSDF(select_file_dir)

    tsdf_dir = './tsdf/tsdf.mat'
    show_TSDF(tsdf_dir, d=0)