#!/usr/bin/python

# View.py
#
# Copyright Michael Graff
#   graff@hm.edu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Updated to remove unknown quanternion reference.
# Using scipy.spatial.tranform.Rotation class instead. Require scipy ver > 1.2
#


import json
from collections import OrderedDict

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

import PYME
from enum import Enum

clipping_dtype = [('x', '<f4', (2,)), ('y', '<f4', (2,)), ('z', '<f4', (2,)), ('v', '<f4', (2,))]
dummy_clipping = np.array([-1e6, 1e6, -1e6, 1e6, -1e6, 1e6, -1e6, 1e6], 'f4').view(clipping_dtype)

def_clip_plane_orientation = np.array([1,0,0,0], 'f8')#np.eye(4,4,dtype='f')

class View(PYME.LMVis.views.View):
    def __init__(self, view_id='id', vec_up=[0,1,0], vec_back = [0,0,1], vec_right = [1,0,0], translation= [0,0,0],
                 scale=1, clipping = dummy_clipping, clip_plane_orientation=def_clip_plane_orientation, clip_plane_position=[0,0,0],
                 lut_draw=True, scale_bar=1000., background_color=[0,0,0], axes_visible=True,
                #  layer0_alpha=1.0, layer0_point_size=30.0,
                 layers=[],
                 **kwargs):
        #avoid args catches for easier debugging
        """
        
        Parameters
        ----------
        view_id     is up to you, as long as serializable with json
        vec_up      np.array
        vec_back    np.array
        vec_right   np.array
        translation np.array
        zoom        usually a scalar
        """
#        super(View, self).__init__() #no reason to call it with the current design
        self._view_id = view_id
        self.vec_up = np.array(vec_up, dtype=np.float)
        self.vec_back = np.array(vec_back, dtype=np.float)
        self.vec_right = np.array(vec_right, dtype=np.float)
#        self.rotation = Rotation.from_dcm([vec_up, vec_back, vec_right])
#        print(vec_up, vec_back, vec_right)
#        print(self.rotation.as_dcm())        
        
        self.translation = np.array(translation, dtype=np.float)
        self.scale = float(scale)
#        print(clipping)
#        print(type(clipping))
        if isinstance(clipping, np.ndarray) and (clipping.dtype == clipping_dtype):
            self.clipping = np.copy(clipping)
        else:
            self.clipping= np.array(clipping, 'f4').squeeze().view(clipping_dtype)
            
        self._clip_plane_orientation = Rotation.from_quat(clip_plane_orientation)
            
        self.clip_plane_position = np.array(clip_plane_position, dtype=np.float)
        
        self.lut_draw = bool(lut_draw)
        self.scale_bar = float(scale_bar)
        self.background_color = np.array(background_color, dtype=np.float)
        self.axes_visible = bool(axes_visible)
        
        # self.layer0_alpha = layer0_alpha
        # self.layer0_point_size = layer0_point_size
        self.layers = layers
        
#        self.update_rotation()
#        self.dirty = False
        
#    def update_rotation(self):
#        self.rotation = Rotation.from_dcm([self.vec_up, self.vec_back, self.vec_right])
        
    @property
    def view_id(self):
        return self._view_id

    @view_id.setter
    def view_id(self, value):
        if value:
            self._view_id = value

#    @property
#    def vec_up(self):
#        if self.dirty:
#            self.update_rotation()
#        return self.rotation.as_dcm()[0]
#    
#    @vec_up.setter
#    def vec_up(self, value):
#        current_rotation = self.rotation.as_dcm()
##        print(current_rotation)
#        current_rotation[0] = value# * 1e10 # hack to enforce rotation
#        np.round(current_rotation, 6, current_rotation)
#        self.rotation = Rotation.from_dcm(current_rotation)
#    
#    @property
#    def vec_back(self):
#        return self.rotation.as_dcm()[1]
#    
#    @vec_back.setter
#    def vec_back(self, value):
#        current_rotation = self.rotation.as_dcm()
#        current_rotation[1] = value# * 1e10
#        np.round(current_rotation, 6, current_rotation)
#        self.rotation = Rotation.from_dcm(current_rotation)
#    
#    @property
#    def vec_right(self):
#        return self.rotation.as_dcm()[2]
#    
#    @vec_right.setter
#    def vec_right(self, value):
#        current_rotation = self.rotation.as_dcm()
#        current_rotation[2] = value# * 1e10
#        np.round(current_rotation, 6, current_rotation)
#        self.rotation = Rotation.from_dcm(current_rotation)
    
    @property
    def clip_plane_orientation(self):
        return self._clip_plane_orientation.as_quat()
    
    # @property
    # def translation(self):
    #     return self._translation
    #
    # @property
    # def zoom(self):
    #     return self._zoom

    def __add__(self, other):
        raise NotImplementedError ()
        
    def __sub__(self, other):
        raise NotImplementedError ()
#
    def __mul__(self, scalar):
        raise NotImplementedError ()
#
    def __div__(self, scalar):
        raise NotImplementedError ()

    def normalize_view(self):
        raise NotImplementedError ()

    def to_json(self):
        ordered_dict = OrderedDict()
        ordered_dict['view_id'] = self.view_id
        ordered_dict['vec_up'] = self.vec_up.tolist()
        ordered_dict['vec_back'] = self.vec_back.tolist()
        ordered_dict['vec_right'] = self.vec_right.tolist()
        ordered_dict['translation'] = self.translation.tolist()
        ordered_dict['scale'] = self.scale
        ordered_dict['clipping'] = self.clipping.view('8f4').squeeze().tolist()
        ordered_dict['clip_plane_orientation'] = self.clip_plane_orientation.tolist()
        ordered_dict['clip_plane_position'] = self.clip_plane_position.tolist()
        
        ordered_dict['lut_draw'] = self.lut_draw
        ordered_dict['scale_bar'] = self.scale_bar
        ordered_dict['background_color'] = self.background_color.tolist()
        ordered_dict['axes_visible'] = self.axes_visible
        
        # ordered_dict['layer0_alpha'] = self.layer0_alpha
        # ordered_dict['layer0_point_size'] = self.layer0_point_size
        for i, layer in enumerate(self.layers):
            for key, val in layer.iteritems():
                ordered_dict["layer{}_{}".format(i, key)] = val
        return ordered_dict

#    def __str__(self):
#        return str(self.to_json())

#    @classmethod
#    def decode_json(cls, json_obj):
#        # if '__type__' in json_obj and json_obj['__type__'] == View:
#        return cls(**json_obj)
    
#    @classmethod
#    def copy(cls, view):
#        return cls.decode_json(view.to_json())
        
    def apply_canvas(self, canvas, fast=True):
        # This applies the save settings to the canvas. This probably needs updating when PYME updates.
        
        canvas.set_view(self)
        canvas.LUTDraw = self.lut_draw
        canvas.scaleBarLength = self.scale_bar
        canvas.clear_colour = self.background_color
        canvas.AxesOverlayLayer.visible = self.axes_visible

        for i, layer in enumerate(self.layers):
            if i >= len(canvas.layers):
                print("Not enough layers. Need to add more layers manually to be able to load settings.")
                break
            if fast:
                # These are both 'fast' changes. Points are not recalculated. Works because render engine reads from them every frame.
                if ~np.allclose(layer["alpha"], canvas.layers[i].get_colors()[0, 3]):
                    #crude check to see if alpha is different from current
                    canvas.layers[i]._colors[:, 3] = layer["alpha"]
                canvas.layers[i].trait_set(trait_change_notify=False, **{'point_size':layer["point_size"]})
            else:
                canvas.layers[i].trait_set(trait_change_notify=True, **{'alpha':layer["alpha"], 'point_size':layer["point_size"]})
                canvas.GrandParent.Parent.Refresh()
        
    def lerp(self, other, t):
        # Should be vectorized so that t can be list-like item
        # Low priority while frames < 1000?
        if t<=0:
            return View.copy(self)
        elif t>=1:
            return View.copy(other)
        else:
#            print(self.rotation)
#            print(other.rotation)
#            t = np.atleast_1d(t)
            rotations = Rotation.from_dcm([[self.vec_up, self.vec_back, self.vec_right], [other.vec_up, other.vec_back, other.vec_right]])


            interp_rotations = Slerp([0.0, 1.0], rotations)([t]).as_dcm()[0]
            interp_translation = (1-t) * self.translation + t * other.translation
            interp_scale = (1-t) * self.scale + t * other.scale
            interp_clipping = ((1-t) * self.clipping.view('8f4') + t * other.clipping.view('8f4')).view(clipping_dtype)[0]

            interp_clip_plane_orientation = Slerp([0.0, 1.0], Rotation.from_quat([self._clip_plane_orientation.as_quat(), other._clip_plane_orientation.as_quat()]))([t]).as_quat()[0]
            interp_clip_plane_position = (1-t) * self.clip_plane_position + t * other.clip_plane_position
            
            binary_interp = t < 0.5
            interp_lut_draw = self.lut_draw if binary_interp else other.lut_draw
            interp_scale_bar = self.scale_bar if binary_interp else other.scale_bar
            interp_axes_visible = self.axes_visible if binary_interp else other.axes_visible
            
            interp_background_color = (1-t) * self.background_color + t * other.background_color
            
            interp_layer0_alpha = (1-t) * self.layer0_alpha + t * other.layer0_alpha
            interp_layer0_point_size = (1-t) * self.layer0_point_size + t * other.layer0_point_size
            
            return View(None,
                        interp_rotations[0],
                        interp_rotations[1],
                        interp_rotations[2],
                        interp_translation,
                        interp_scale,
                        interp_clipping,
                        interp_clip_plane_orientation,
                        interp_clip_plane_position,
                        interp_lut_draw,
                        interp_scale_bar,
                        interp_background_color,
                        interp_axes_visible,
                        interp_layer0_alpha,
                        interp_layer0_point_size,
                        )
    
    @classmethod
    def rotate(cls, view, axis, degree):
        current_rotation = Rotation.from_dcm([view.vec_up, view.vec_back, view.vec_right])
        new_rotation = np.zeros(3, np.float)
        new_rotation[axis] = np.deg2rad(degree)
        combined_rotation = current_rotation * Rotation.from_rotvec(new_rotation)
        combined_rotation_dcm = combined_rotation.as_dcm()
        view.vec_up = combined_rotation_dcm[0]
        view.vec_back = combined_rotation_dcm[1]
        view.vec_right = combined_rotation_dcm[2]
    
  

class VideoView(View):
    JSON_DURATION = 'duration'
    
    class Interp_mode(Enum):
        LINEAR = 0
        SQUARE = 1
        SQUARE_ROOT = 2
        SMOOTH_STEP_A = 3
        SMOOTH_STEP_B = 4
    
    def __init__(self, view_id='id', vec_up=[0,1,0], vec_back = [0,0,1], vec_right = [1,0,0], translation= [0,0,0], scale=1,
                 clipping=dummy_clipping,
                 duration = 1.0, interp_mode=Interp_mode.SMOOTH_STEP_B.name,
#                 lut_draw=True, scale_bar=1000., background_color=[0,0,0],
                 *args, **kwargs):
        """

        Parameters
        ----------
        view_id     is up to you, as long as serializable with json
        vec_up      np.array
        vec_back    np.array
        vec_right   np.array
        translation np.array
        zoom        usually a scalar
        duration    duration of the view transition in seconds
        """
        super(VideoView, self).__init__(view_id, vec_up, vec_back, vec_right, translation, scale, clipping,
#             lut_draw, scale_bar, background_color,
             *args, **kwargs)
        self._duration = float(duration)
        self.interp_mode = VideoView.Interp_mode[interp_mode]
        
    @classmethod
    def from_canvas(cls, canvas, vec_id, duration=1.0, interp_mode=Interp_mode.SMOOTH_STEP_B):
        # reads state from canvas
        # Probably needs updating when PYME updates
        view = canvas.get_view(vec_id) #already a copy, but copy again anyway in case base code changes, can be the basic View class. Not for copying
        args = list([view.view_id,
                   view.vec_up,
                   view.vec_back,
                   view.vec_right,
                   view.translation,
                   view.scale,
                   view.clipping,
                   duration,
                   interp_mode.name,
                   view.clip_plane_orientation,
                   view.clip_plane_position,])
#        print(canvas.AxesOverlayLayer)
        args.extend([canvas.LUTDraw,
                     canvas.scaleBarLength,
                     canvas.clear_colour,
                     canvas.AxesOverlayLayer.visible,
                    #  canvas.layers[0].alpha,
                    #  canvas.layers[0].point_size,
                ])
        layers_args = list()
        for layer in canvas.layers:
            temp_dict = OrderedDict()
            temp_dict["alpha"] = layer.alpha
            temp_dict["point_size"] = layer.point_size
            layers_args.append(temp_dict)
        args.append(layers_args)

        return cls(*args)
        
#    @classmethod
#    def from_view(cls, view, duration=3.0, interp_mode=Interp_mode.SMOOTH_STEP_B):
#        return cls(view.view_id,
#                   view.vec_up,
#                   view.vec_back,
#                   view.vec_right,
#                   view.translation,
#                   view.scale,
#                   view.clipping,
#                   duration,
#                   interp_mode.name,
#                   view.clip_plane_orientation,
#                   view.clip_plane_position,
##                   view.lut_draw,
##                   view.scale_bar,
##                   view.background_color,
#                   )
    
    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        if value:
            self._duration = float(value)
    
    def to_json(self):
        ordered_dict = super(VideoView, self).to_json()
        ordered_dict[self.JSON_DURATION] = self._duration
        ordered_dict['interp_mode'] = self.interp_mode.name
        return ordered_dict
    
    @classmethod
    def decode_json(cls, json_obj):
    #     # if '__type__' in json_obj and json_obj['__type__'] == View:
    #     return VideoView(View.get_json_field(json_obj, View.JSON_VIEW_ID, 'id'),
    #                      View.get_json_array(json_obj, View.JSON_VEC_UP, numpy.array([0, 1, 0])),
    #                      View.get_json_array(json_obj, View.JSON_VEC_BACK, numpy.array([0, 0, 1])),
    #                      View.get_json_array(json_obj, View.JSON_VEC_RIGHT, numpy.array([1, 0, 0])),
    #                      View.get_json_array(json_obj, View.JSON_TRANSLATION, numpy.array([0, 0, 0])),
    #                      View.get_json_field(json_obj, View.JSON_ZOOM, 1),
    #                      View.get_json_field(json_obj, VideoView.JSON_DURATION, 1))
        layers = []
        for key, val in json_obj.items():
            if key.startswith("layer"):
                layer_num = int(key.split("_")[0][5:])
                while layer_num >= len(layers):
                    layers.append(OrderedDict())
                layers[layer_num]["_".join(key.split("_")[1:])] = val
                json_obj.pop(key)

        json_obj["layers"] = layers
        return cls(**json_obj)


if __name__ == '__main__':
    view = View(1, np.array([1, 1, 1]), np.array([2, 2, 2]), np.array([3, 3, 3]),
                np.array([0, 0, 0]), 5)
    a = json.loads(json.dumps(view.to_json()))
    view2 = View.decode_json(a)
