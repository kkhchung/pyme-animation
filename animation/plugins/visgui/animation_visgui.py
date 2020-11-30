#!/usr/bin/python

# VideoPanel.py
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

import json
from time import sleep

import wx
import wx.lib.agw.aui as aui
#import wx.lib.mixins.listctrl

from PYME.ui import editList

from PYME.LMVis.Extras.dockedPanel import DockedPanel
from animation.plugins.views import View, VideoView

from PIL import Image
import os
import numpy as np

from collections import OrderedDict
#from PYME.util import mProfile

# noinspection PyUnusedLocal
class VideoPanel(DockedPanel):
    JSON_LIST_NAME = 'views'

    def __init__(self, parent_panel, **kwargs):
        kwargs['style'] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, parent_panel, **kwargs)

        
#        mProfile.profileOn(["animation_visgui.py"])
        self.snapshots = list()
        self.parent_panel = parent_panel
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)

        self.create_list_control(vertical_sizer)

        self.create_buttons(vertical_sizer)
        
        self.create_nav_panel(vertical_sizer)
        
        self.create_snapshot_details(vertical_sizer)

        self.SetSizerAndFit(vertical_sizer)
        
        self.next_view_id = 0
        
        self.displayed_snapshot_index = -1
        
        # non-critical to save/load settings, fancy function to catch if live changes on layer
        self.get_canvas().layers[0].on_trait_change(self.on_canvas_changed, 'alpha, point_size')
        
    def create_nav_panel(self, sizer):
        # generate the buttons
        skip = wx.StaticText(self, -1, '')
        zoom_in_button = wx.Button(self, -1, label='Zoom +', style=wx.BU_EXACTFIT)
        zoom_out_button = wx.Button(self, -1, label='Zoom -', style=wx.BU_EXACTFIT)
        
        x_increase_button = wx.Button(self, -1, label='Axis X +', style=wx.BU_EXACTFIT)
        x_decrease_button = wx.Button(self, -1, label='Axis X -', style=wx.BU_EXACTFIT)
        y_increase_button = wx.Button(self, -1, label='Axis Y +', style=wx.BU_EXACTFIT)
        y_decrease_button = wx.Button(self, -1, label='Axis Y -', style=wx.BU_EXACTFIT)
        z_increase_button = wx.Button(self, -1, label='Axis Z +', style=wx.BU_EXACTFIT)
        z_decrease_button = wx.Button(self, -1, label='Axis Z -', style=wx.BU_EXACTFIT)
        
        x_rotate_increase_button = wx.Button(self, -1, label='Rot Right', style=wx.BU_EXACTFIT)
        x_rotate_decrease_button = wx.Button(self, -1, label='Rot Left', style=wx.BU_EXACTFIT)
        y_rotate_increase_button = wx.Button(self, -1, label='Rot Back', style=wx.BU_EXACTFIT)
        y_rotate_decrease_button = wx.Button(self, -1, label='Rot Forward', style=wx.BU_EXACTFIT)
        z_rotate_increase_button = wx.Button(self, -1, label='Rot Up', style=wx.BU_EXACTFIT)
        z_rotate_decrease_button = wx.Button(self, -1, label='Rot Down', style=wx.BU_EXACTFIT)
        
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_scale(e, True), zoom_in_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_scale(e, False), zoom_out_button)
        
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 0, True), x_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 0, False), x_decrease_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 1, True), y_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 1, False), y_decrease_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 2, True), z_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_translate(e, 2, False), z_decrease_button)
        
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 0, True), x_rotate_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 0, False), x_rotate_decrease_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 1, True), y_rotate_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 1, False), y_rotate_decrease_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 2, True), z_rotate_increase_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.on_rotate(e, 2, False), z_rotate_decrease_button)
        
        grid_sizer = wx.GridSizer(5, 3, 0, 0)
        grid_sizer.Add(zoom_in_button, flag=wx.EXPAND)
        grid_sizer.Add(zoom_out_button, flag=wx.EXPAND)
        grid_sizer.Add(skip, flag=wx.EXPAND)
        
        grid_sizer.Add(x_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(y_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(z_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(x_decrease_button, flag=wx.EXPAND)
        grid_sizer.Add(y_decrease_button, flag=wx.EXPAND)
        grid_sizer.Add(z_decrease_button, flag=wx.EXPAND)
        
        grid_sizer.Add(x_rotate_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(y_rotate_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(z_rotate_increase_button, flag=wx.EXPAND)
        grid_sizer.Add(x_rotate_decrease_button, flag=wx.EXPAND)
        grid_sizer.Add(y_rotate_decrease_button, flag=wx.EXPAND)
        grid_sizer.Add(z_rotate_decrease_button, flag=wx.EXPAND)
        
        sizer.Add(grid_sizer, 0, wx.EXPAND, 0)
        
    def on_scale(self, event, increase):
        modifier = 2.0 if increase else 0.5
        if wx.GetKeyState(wx.WXK_CONTROL) and not wx.GetKeyState(wx.WXK_SHIFT):            
            modifier *= 10.0
        elif not wx.GetKeyState(wx.WXK_CONTROL) and wx.GetKeyState(wx.WXK_SHIFT):    
            modifier *= 0.1
            
        self.get_canvas().view.scale *= modifier
        self.get_canvas().Refresh()
        
    def on_translate(self, event, axis, increase):
        modifier = 1000.0 if increase else -1000.0
        if wx.GetKeyState(wx.WXK_CONTROL) and not wx.GetKeyState(wx.WXK_SHIFT):            
            modifier *= 10.0
        elif not wx.GetKeyState(wx.WXK_CONTROL) and wx.GetKeyState(wx.WXK_SHIFT):    
            modifier *= 0.1
            
        self.get_canvas().view.translation[axis] += modifier
        self.get_canvas().Refresh()
    
    def on_rotate(self, event, axis, increase):
        modifier = 45.0 if increase else -45.0
        if wx.GetKeyState(wx.WXK_CONTROL) and not wx.GetKeyState(wx.WXK_SHIFT):            
            modifier *= 8. / 3.
        elif not wx.GetKeyState(wx.WXK_CONTROL) and wx.GetKeyState(wx.WXK_SHIFT):    
            modifier *= 2. / 3.
            
        View.rotate(self.get_canvas().view, axis, modifier)
        self.get_canvas().Refresh()
        
    def create_snapshot_details(self, sizer):
#        class EditableListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.TextEditMixin):
#            def __init__(self, *args, **kwargs):                
#                wx.ListCtrl.__init__(self, *args, **kwargs)
#                wx.lib.mixins.listctrl.TextEditMixin.__init__(self)
        
        self.details_table = editList.EditListCtrl(self, -1,
                              style=wx.BU_EXACTFIT | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER | wx.LC_EDIT_LABELS)
        
        self.details_table.InsertColumn(0, 'param', width=100)
        self.details_table.InsertColumn(1, 'value', width=150)
        self.details_table.makeColumnEditable(1)
        
        self.details_table.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.on_snapshot_details_change)
        
        sizer.Add(self.details_table, 0, wx.EXPAND, 0)
        
    def on_snapshot_details_change(self, event):
        key = self.details_table.GetItemText(event.m_itemIndex)
        value_new = event.GetLabel()

        print(key)
        print(value_new)
        try:
            value_new = eval(value_new)
        except Exception as e:
            print(e)
            pass
        
        try:

            dump = VideoView(**{key: value_new})
#            print(dump)
            
            json_dict = OrderedDict()
            for i in range(self.details_table.GetItemCount()):
                val = self.details_table.GetItemText(i, 1)

                try:
                    val = eval(val)
                except Exception as e:
                    print(e)
                    pass
    
                json_dict[self.details_table.GetItemText(i, 0)] = val
                
            json_dict[key] = value_new
                
            view = VideoView(**json_dict)
            self.snapshots[self.displayed_snapshot_index] = view
            self.refill()
            view.apply_canvas(self.get_canvas(), fast=False)
            print('updated')
            
        except Exception as e:
            event.Veto()
            print(e)
#            raise(e)
        
    def create_list_control(self, sizer):
        self.view_table = wx.ListCtrl(self, -1,
                              style=wx.BU_EXACTFIT | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER)

        self.view_table.InsertColumn(0, 'id', width=50)
        self.view_table.InsertColumn(1, 'duration', width=50)
        self.view_table.InsertColumn(2, 'interp mode', width=150)
        
        self.view_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_edit)
        self.view_table.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_view)
        self.view_table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_view)
        
        sizer.Add(self.view_table, 0, wx.EXPAND, 0)

    def create_buttons(self, vertical_sizer):
        grid_sizer = wx.GridSizer(4, 5, 0, 0)
        # generate the buttons
        add_button = wx.Button(self, -1, label='Add', style=wx.BU_EXACTFIT)
        add_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_BUTTON))
        delete_button = wx.Button(self, -1, label='Delete', style=wx.BU_EXACTFIT)
        delete_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_MINUS, wx.ART_BUTTON))
        skip = wx.StaticText(self, -1, '')
        list_shift_up_button = wx.Button(self, -1, label='Up', style=wx.BU_EXACTFIT)
        list_shift_down_button = wx.Button(self, -1, label='Down', style=wx.BU_EXACTFIT)
        load_button = wx.Button(self, -1, label='Load', style=wx.BU_EXACTFIT)
        load_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_BUTTON))
        save_button = wx.Button(self, -1, label='Save', style=wx.BU_EXACTFIT)
        save_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_BUTTON))
        clear_button = wx.Button(self, -1, label='Clear', style=wx.BU_EXACTFIT)
        clear_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_BUTTON))
        run_button = wx.Button(self, -1, label='Play', style=wx.BU_EXACTFIT)
        make_button = wx.Button(self, -1, label='Make', style=wx.BU_EXACTFIT)
        self.stop_button = wx.Button(self, -1, label='Canel', style=wx.BU_EXACTFIT)
        self.stop_button.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_BUTTON))  
        self.stop_button.Enable(False)
        
        width_label = wx.StaticText(self, label='Width:', style=wx.BU_EXACTFIT | wx.EXPAND | wx.ALIGN_CENTRE)
        self.width_text = wx.TextCtrl(self, size=(-1, -1), style=wx.BU_EXACTFIT | wx.EXPAND)
        self.width_text.SetValue(str(-1))
        height_label = wx.StaticText(self, label='Height:', style=wx.BU_EXACTFIT | wx.EXPAND | wx.ALIGN_CENTRE)
        self.height_text = wx.TextCtrl(self, size=(-1, -1), style=wx.BU_EXACTFIT | wx.EXPAND)
        self.height_text.SetValue(str(-1))
        framerate_label = wx.StaticText(self, label='FPS:', style=wx.BU_EXACTFIT | wx.EXPAND | wx.ALIGN_CENTRE)
        self.framerate_text = wx.TextCtrl(self, size=(-1, -1), style=wx.BU_EXACTFIT | wx.EXPAND)
        self.framerate_text.SetValue(str(30.0))

        # bind the buttons and its handlers
        self.Bind(wx.EVT_BUTTON, self.add_snapshot, add_button)
        self.Bind(wx.EVT_BUTTON, self.delete_snapshot, delete_button)
        self.Bind(wx.EVT_BUTTON, self.clear, clear_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.shift_snapshot_order(e, True), list_shift_up_button)
        self.Bind(wx.EVT_BUTTON, lambda e: self.shift_snapshot_order(e, False), list_shift_down_button)
        self.Bind(wx.EVT_BUTTON, self.load, load_button)
        self.Bind(wx.EVT_BUTTON, self.save, save_button)
        self.Bind(wx.EVT_BUTTON, self.run, run_button)
        self.Bind(wx.EVT_BUTTON, self.make, make_button)
        self.Bind(wx.EVT_BUTTON, self.stop_animation, self.stop_button)


        # add_snapshot the buttons to the view
        grid_sizer.Add(add_button, flag=wx.EXPAND)
        grid_sizer.Add(delete_button, flag=wx.EXPAND)
#        grid_sizer.Add(skip)
        grid_sizer.Add(clear_button, flag=wx.EXPAND)
        grid_sizer.Add(list_shift_up_button, flag=wx.EXPAND)
        grid_sizer.Add(list_shift_down_button, flag=wx.EXPAND)

        grid_sizer.Add(save_button, flag=wx.EXPAND)
        grid_sizer.Add(load_button, flag=wx.EXPAND)
        grid_sizer.Add(run_button, flag=wx.EXPAND)
        grid_sizer.Add(make_button, flag=wx.EXPAND)
        grid_sizer.Add(self.stop_button, flag=wx.EXPAND)
#        grid_sizer.Add(skip)
        
        grid_sizer.Add(width_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.width_text, flag=wx.EXPAND)
        grid_sizer.Add(height_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.height_text, flag=wx.EXPAND)
        grid_sizer.Add(skip, flag=wx.EXPAND)
        grid_sizer.Add(framerate_label, flag=wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.framerate_text, flag=wx.EXPAND)
        
        vertical_sizer.Add(grid_sizer)
        
    def shift_snapshot_order(self, event, forward):
        index = self.view_table.GetFirstSelected()
        if index != -1:
            new_index = index + (-1 if forward else 1)
            if new_index >= 0 and new_index < len(self.snapshots):            
                self.snapshots.insert(new_index, self.snapshots.pop(index))
                self.refill()
                self.view_table.Select(new_index)

    def add_snapshot_to_list(self, snapshot):
        self.snapshots.append(snapshot)
        self.refill()

    def add_snapshot(self, event):

        view_id = 'view_%d' % self.next_view_id
        self.next_view_id += 1
        if view_id:
#            duration = 3.0
#            view = self.get_canvas().get_view(vec_id)
#            video_view = VideoView.from_view(view)#, duration, )
            video_view = VideoView.from_canvas(self.get_canvas(), view_id)#, duration, )
            self.add_snapshot_to_list(video_view)

    def delete_snapshot(self, event):
        index = self.view_table.GetFirstSelected()
        if index >= 0:
            del self.snapshots[index]
        self.refill()

    def clear(self, event):
        self.snapshots[:] = []
        self.view_table.DeleteAllItems()

    def clear_view(self):
        self.view_table.DeleteAllItems()

    def save(self, event):
        file_name = wx.FileSelector('Save view as json named... ', wildcard="JSON file (*.json)|*.json" ,flags=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if file_name:
            if not file_name.endswith('.json'):
                file_name = '{}.json'.format(file_name)
            with open(file_name, 'w') as f:
                snapshots = [snapshot.to_json() for snapshot in self.snapshots]
                f.writelines(json.dumps({self.JSON_LIST_NAME: snapshots}, indent=4))

    def load(self, event):
        file_name = wx.FileSelector('Open View-JSON file', wildcard="JSON file (*.json)|*.json")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
                for view in data[self.JSON_LIST_NAME]:
                    self.add_snapshot_to_list(VideoView.decode_json(view))

    def make(self, event):
        self.play(True)        

    def run(self, event):
        self.play(False)
        
    def build_view_list(self, fps):
        view_list = list()

        current_view = self.snapshots[0]
        for i, view in enumerate(self.snapshots):

            if i==0:
                t = [1.0]
            else:
                t = np.linspace(0, 1.0, (view.duration * fps)+1)
                if view.interp_mode == VideoView.Interp_mode.LINEAR:
                    pass
                elif view.interp_mode == VideoView.Interp_mode.SQUARE:
                    t = t*t
                elif view.interp_mode == VideoView.Interp_mode.SQUARE_ROOT:
                    t = np.sqrt(t)
                elif view.interp_mode == VideoView.Interp_mode.SMOOTH_STEP_A:
                    t = t*t*(3 - 2*t)
                elif view.interp_mode == VideoView.Interp_mode.SMOOTH_STEP_B:
                    t = t*t*t*(6*t*t - 15*t + 10)
                
            for j, ti in enumerate(t):

                if np.isclose(ti, 0.0):
                    continue
                new_view = current_view.lerp(view, ti)
                view_list.append(new_view)
                
            current_view = view
        
        return view_list

    def play(self, save):
        for child1 in self.parent_panel.GetChildren():
            for child2 in child1.GetChildren():
                child2.Enable(False)
        self.stop_button.Enable()
        
        try:
            fps = float(self.framerate_text.GetValue())
        except:
#            self.framerate_text.SetValue(str(30.0))            
            fps = 30.0
            print("Bad FPS input. Defaulting to 30 fps.")
        
        if len(self.snapshots) == 0:
            self.add_snapshot(None)
        view_list = self.build_view_list(fps)
        
        self.old_width, self.old_height = self.get_canvas().Size
        width = self.width_text.GetValue()
        height = self.height_text.GetValue()
        try:
            width = int(width)
            height = int(height)
            
            if width>0 and height>0:
                self.get_canvas().SetSize((width, height))

        except:
            width = self.old_width
            height = self.old_height
            print("Bad width/height input. Defaulting to current size.")
                
        self.get_canvas().displayMode = '3D'
        
        if save:
            try:
                import cv2
                fourcc = cv2.VideoWriter_fourcc(*"MP4V")
                
                dir_name = wx.DirSelector()
                if dir_name != '':
                    video = cv2.VideoWriter(os.path.join(dir_name, "video.mp4"), fourcc, fps, tuple(self.get_canvas().Size))
                else:
                    save = False
            except ImportError:
                msg_text = 'OpenCV 2 is needed to save videos. Please install: \"conda install -c menpo opencv\"'
                msg = wx.MessageDialog(self, msg_text, 'Missing package', wx.OK | wx.ICON_WARNING)
                msg.ShowModal()
                msg.Destroy()
                #return
                save=False

        self.view_counter = 0
        self.view_list = view_list        
        self.halt = False
        
        if save:            
            for i in range(len(self.view_list)):
#                print(self.halt)
                if self.halt == True:
                    break
#                self.get_canvas().set_view(self.view_list[i])
                self.view_list[i].apply_canvas(self.get_canvas())
                snap = self.get_canvas().getIm()[:, ::-1, :]
                snap = (255*snap).astype('uint8').transpose(1, 0, 2)
                video.write(snap.astype(np.uint8)[:,:, [2,1,0]])
                im = Image.fromarray(snap).save(os.path.join(dir_name, 'frame_{0:06d}.jpg'.format(i)))
                wx.Yield()
            
            video.release()

            
            self.play_finish()
        else:
            self.timer = wx.Timer(self)

            self.Bind(wx.EVT_TIMER, self.play_views, self.timer)
            self.timer.Start(1e3/fps)
#            print('timer started')
            

    def play_views(self, event):
        if self.view_counter >= 0 and self.view_counter < len(self.view_list):
#            self.get_canvas().set_view(self.view_list[self.view_counter])
            self.view_list[self.view_counter].apply_canvas(self.get_canvas())
            self.view_counter += 1
        else:
            self.timer.Stop()
            self.play_finish()
            
            
    def play_finish(self):
        if self.old_width != self.get_canvas().Size[0] or self.old_height != self.get_canvas().Size[1]:
            self.get_canvas().SetSize((self.old_width, self.old_height))
        
        if self.halt or self.view_counter==-1 :
            print("Terminated")
        else:
            print("Animation completed. Total {} frames".format(len(self.view_list)))
        
        for child1 in self.parent_panel.GetChildren():
            for child2 in child1.GetChildren():
                child2.Enable(True)
                
        self.stop_button.Enable(False)
            
#        mProfile.profileOff()
#        mProfile.report()
        
    def stop_animation(self, event):
#        print('cancel clicked')
        self.halt = True
        self.view_counter = -1
        
        # hard refresh, for when an exception is raised and play_finish is never called.
        if wx.GetKeyState(wx.WXK_CONTROL):
            self.play_finish()

    # noinspection PyTypeChecker
    def on_edit(self, event):
        snapshot = self.snapshots[self.view_table.GetFirstSelected()]

        dlg = EditDialog(self, snapshot, 'Edit VideoView')
        ret = dlg.ShowModal()

        if ret == wx.ID_OK:
            name = dlg.get_name()
            duration = dlg.get_duration()
            interp_mode = dlg.get_interp_mode()

            snapshot.view_id = name
            snapshot.duration = duration
            snapshot.interp_mode = interp_mode

        dlg.Destroy()
        self.refill()
        
    def on_canvas_changed(self, *args, **kwargs):

        index = self.view_table.GetFirstSelected()
        if index != -1:            
            self.snapshots[index] = VideoView.from_canvas(self.get_canvas(), self.snapshots[index].view_id)
            self.on_select_view(None)

    def on_select_view(self, event):
        index = self.view_table.GetFirstSelected()
        snapshot = self.snapshots[index]

#        self.get_canvas().set_view(snapshot)
        snapshot.apply_canvas(self.get_canvas(), fast=False)
        
        self.fill_details_table(snapshot)
        
        self.displayed_snapshot_index = index
        
    def on_deselect_view(self, event):
        canvas = self.get_canvas()
        canvas.set_view(View.copy(canvas.get_view()))
        self.details_table.DeleteAllItems()
        
    def fill_details_table(self, snapshot):
#        self.details_table.DeleteAllItems()
        
        json_dict = snapshot.to_json()        
        for i, key in enumerate(json_dict.keys()):
            j = self.details_table.InsertItem(i, key)
            self.details_table.SetItem(j, 1, str(json_dict[key]))
            
    def refill(self):
        self.clear_view()
        for i, snapshot in enumerate(self.snapshots):
            index = len(self.snapshots)
            j = self.view_table.InsertItem(index, snapshot.view_id)
            if i > 0:
                self.view_table.SetItem(j, 1, str(snapshot.duration))
                self.view_table.SetItem(j, 2, snapshot.interp_mode.name)
            
#    def refresh_visgui(self):
        

class EditDialog(wx.Dialog):
    def __init__(self, parent, snapshot, title=''):
        """

        Returns
        -------
        EditDialog
        """
        wx.Dialog.__init__(self, parent, title=title, size=(400, 300), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        sizer1 = wx.BoxSizer(wx.VERTICAL)

        self.edit_panel = EditPanel(self, -1, snapshot, pos=(0, 0), size=(-1, -1))
        sizer1.Add(self.edit_panel, 0, wx.ALL | wx.EXPAND, 5)

        # create button
        bt_sizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()

        bt_sizer.AddButton(btn)

        bt_sizer.Realize()

        sizer1.Add(bt_sizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # set total size
        self.SetSizer(sizer1)
        sizer1.Fit(self)

    def get_name(self):
        return self.edit_panel.id

    def get_duration(self):
        return self.edit_panel.duration
    
    def get_interp_mode(self):
        return self.edit_panel.interp_mode


class EditPanel(wx.Panel):
    def __init__(self, parent, id_number, snapshot, size, pos):
        wx.Panel.__init__(self, parent, id_number, size=size, pos=pos, style=wx.BORDER_SUNKEN)
        grid_sizer = wx.GridSizer(3, 2, 0, 0)

        # generate row for view_id
        grid_sizer.Add(wx.StaticText(self, label='View Id', style=wx.BU_EXACTFIT))
        self.name_text = wx.TextCtrl(self, size=(-1, -1), style=wx.BU_EXACTFIT | wx.EXPAND)
        self.name_text.SetValue(snapshot.view_id)
        grid_sizer.Add(self.name_text)

        # generate row for duration
        grid_sizer.Add(wx.StaticText(self, label='Duration', style=wx.BU_EXACTFIT))
        self.duration_text = wx.TextCtrl(self, size=(-1, -1), style=wx.BU_EXACTFIT | wx.EXPAND)
        grid_sizer.Add(self.duration_text)
        self.duration_text.SetValue("{:.9f}".format(snapshot.duration))
        
        grid_sizer.Add(wx.StaticText(self, label='Interp mode', style=wx.BU_EXACTFIT))
        self.interp_mode_cb = wx.ComboBox(self, size=(-1, -1), value=snapshot.interp_mode.name, choices=VideoView.Interp_mode.__members__.keys(), style=wx.BU_EXACTFIT | wx.EXPAND)
        grid_sizer.Add(self.interp_mode_cb)
#        self.interp_mode_text.SetValue("{:.9f}".format(snapshot.interp_mode.name))

        self.SetSizerAndFit(grid_sizer)

    @property
    def id(self):
        return self.name_text.GetValue()

    @property
    def duration(self):
        try:
            return float(self.duration_text.GetValue())
        except ValueError:
            return None

    @property
    def interp_mode(self):
#        return VideoView.Interp_mode[self.interp_mode_cb.GetStringSelection()]
        return VideoView.Interp_mode[VideoView.Interp_mode.__members__.keys()[self.interp_mode_cb.GetSelection()]]


class VideoFrame(wx.Frame):
    def __init__(self, parent_frame):
        wx.Frame.__init__(self, parent_frame, title='Display')

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dispPanel = VideoPanel(self)

        hsizer.Add(self.dispPanel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(hsizer)
        hsizer.Fit(self)

def Plug(vis_fr):
    
    def show(vis_fr, panel, p_info_name, caption):
        frame_manager = vis_fr._mgr
        panel.SetSize(panel.GetBestSize())
        p_info = aui.AuiPaneInfo().Name(p_info_name).Right().Caption(caption).CloseButton(True).MinimizeButton(
            True).DestroyOnClose(True).Dock().MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART | aui.AUI_MINIMIZE_POS_RIGHT)
        frame_manager.AddPane(panel, p_info)
        frame_manager.ShowPane(panel, True)
    
#    DockedPanel.add_menu_item(vis_fr, 'Animation', VideoPanel, 'animation_panel')
    vis_fr.AddMenuItem('Kenny', 'Animation', lambda e: show(vis_fr, VideoPanel(vis_fr), 'animation_panel', 'Animation'),
                  helpText='')

