import numpy as np
from scipy.spatial import cKDTree as KDTree
from scipy.spatial import Voronoi
from pypolycontain.utils.random_polytope_generator import get_k_random_edge_points_in_zonotope

def build_key_point_kd_tree(polytopes, key_vertex_count = 0, distance_scaling_array=None):
    if key_vertex_count > 0:
        n = len(polytopes)*(1+2**key_vertex_count)
    else:
        n = len(polytopes)
    if polytopes[0].__name__=='AH_polytope':
        dim = polytopes[0].t.shape[0]
    elif polytopes[0].__name__=='zonotope':
        dim = polytopes[0].x.shape[0]
    else:
        raise NotImplementedError
    key_point_to_zonotope_map = dict()
    scaled_key_points = np.zeros((n,dim))
    if distance_scaling_array is None:
        distance_scaling_array = np.ones(n)
    for i, p in enumerate(polytopes):
        if p.__name__=='AH_polytope' and key_vertex_count==0:
            scaled_key_points[i,:] = np.multiply(distance_scaling_array, p.t[:, 0], dtype='float')
            if str(p.t[:, 0]) not in key_point_to_zonotope_map:
                key_point_to_zonotope_map[str(p.t[:, 0])]=[p]
            else:
                key_point_to_zonotope_map[str(p.t[:, 0])].append(p)
        elif p.__name__ == 'zonotope' and key_vertex_count==0:
            scaled_key_points[i,:] = np.multiply(distance_scaling_array, p.x[:, 0], dtype='float')
            key_point_to_zonotope_map[str(p.x[:, 0])]=[p]
        elif p.__name__=='zonotope':
            scaled_key_points[i*(1+2**key_vertex_count),:] = np.multiply(distance_scaling_array, p.x[:, 0], dtype='float')
            key_point_to_zonotope_map[str(p.x[:, 0])]=[p]
            other_key_points = get_k_random_edge_points_in_zonotope(p, key_vertex_count)
            scaled_other_key_points = np.multiply(distance_scaling_array, other_key_points, dtype='float')
            scaled_key_points[i * (2 ** key_vertex_count + 1) + 1:(i + 1) * (2 ** key_vertex_count + 1),
            :] = scaled_other_key_points
            for kp in other_key_points:
                key_point_to_zonotope_map[str(kp)] = [p]
        else:
            raise NotImplementedError
    return KDTree(scaled_key_points),key_point_to_zonotope_map

def update_key_point_kd_tree(polytopes, scaled_key_point_tree, key_point_to_zonotope_map, key_vertex_count = 0, distance_scaling_array=None):
    if key_vertex_count > 0:
        n = len(polytopes)*(1+2**key_vertex_count)
    else:
        n = len(polytopes)
    if polytopes[0].__name__=='AH_polytope':
        dim = polytopes[0].t.shape[0]
    else:
        raise NotImplementedError
    scaled_key_points = np.zeros((n,dim))
    if distance_scaling_array is None:
        distance_scaling_array = np.ones(n)
    
    kdtree_old_data = scaled_key_point_tree.data.reshape(-1, dim)

    # update key_point_to_zonotope_map
    for i, p in enumerate(polytopes):
        if p.__name__=='AH_polytope' and key_vertex_count==0:
            scaled_key_points[i,:] = np.multiply(distance_scaling_array, p.t[:, 0], dtype='float')
            if str(p.t[:, 0]) not in key_point_to_zonotope_map:
                key_point_to_zonotope_map[str(p.t[:, 0])]=[p]
            else:
                key_point_to_zonotope_map[str(p.t[:, 0])].append(p)
        else:
            raise NotImplementedError

    kdtree_new_data = np.concatenate((kdtree_old_data, scaled_key_points), axis=0)
    return KDTree(kdtree_new_data),key_point_to_zonotope_map

def build_polyotpe_centroid_voronoi_diagram(polytopes):
    n = len(polytopes)
    if polytopes[0].type=='AH_polytope':
        k = polytopes[0].t.shape[0]
    elif polytopes[0].type=='zonotope':
        k = polytopes[0].x.shape[0]
    else:
        raise NotImplementedError
    centroids = np.zeros((n, k))
    for i, z in enumerate(polytopes):
        if polytopes[0].type == 'AH_polytope':
            centroids[i, :] = polytopes[i].t[:,0]
        elif polytopes[0].type == 'zonotope':
            centroids[i, :] = polytopes[i].x[:,0]
        else:
            raise NotImplementedError
    return Voronoi(centroids)
