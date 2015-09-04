import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import kivent_core
import kivent_particles
from os import walk
from os.path import join, dirname, split, splitext
from kivent_core.managers.resource_managers import texture_manager
from flat_kivy.flatapp import FlatApp
from flat_kivy.uix.behaviors import (TouchRippleBehavior, GrabBehavior, 
    ButtonBehavior)
from kivy.properties import (NumericProperty, StringProperty, DictProperty, 
    ObjectProperty, ListProperty)
from flat_kivy.font_definitions import style_manager
from kivy.metrics import dp, sp
from flat_kivy.uix.flattogglebutton import FlatToggleButton
from flat_kivy.uix.flatpopup import FlatPopup
from flat_kivy.uix.flatlabel import FlatLabel
from kivy.vector import Vector
from math import atan2, degrees
import re
import string


def get_all_files(dir_name, extension):
    output = []
    output_a = output.append
    for root, dirs, files in walk(dir_name):
        for fl in files:
            if fl.endswith(extension): 
                output_a(join(root,fl))
    return output

images_to_load = get_all_files(
    join(dirname(__file__), 'assets', 'particle_graphics', 'image'), '.png')

for im_add in images_to_load:
    texture_manager.load_image(im_add)


class EditorPanel(FloatLayout):
    pass


class EditorScreen(Screen):
    pass


class SliderWithValues(BoxLayout):
    minimum = NumericProperty(0.)
    maximum = NumericProperty(100.)
    step = NumericProperty(1.)
    current_value = NumericProperty(0.)
    font_group_id = StringProperty('default')

    def increment_slider(self):
        slider = self.ids.slider
        if slider.value + self.step <= self.maximum:
            slider.value += self.step

    def decrement_slider(self):
        slider = self.ids.slider
        if slider.value - self.step >= self.minimum:
            slider.value -= self.step


class TextureChoiceButton(GrabBehavior, ButtonBehavior, TouchRippleBehavior, 
    BoxLayout):
    font_group_id = StringProperty(None)
    texture_name = StringProperty(None)
    texture = ObjectProperty(None)

class EffectChoiceButton(GrabBehavior, ButtonBehavior, TouchRippleBehavior,
    BoxLayout):
    choice_name = StringProperty(None)
    font_group_id = StringProperty(None)


class NamedValueSlider(BoxLayout):
    minimum = NumericProperty(0.)
    maximum = NumericProperty(100.)
    step = NumericProperty(1.)
    current_value = NumericProperty(0.)
    font_group_id = StringProperty('default')
    slider_name = StringProperty('default')
    field_name = StringProperty('')
    field_count = NumericProperty(1)
    slider_group = ObjectProperty(None)


class ScreenToggleButton(FlatToggleButton):
    screen_name = StringProperty(None)


class CustomPopup(FlatPopup):
    pass


class TouchConsumingStackLayout(StackLayout):
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            super(TouchConsumingStackLayout, self).on_touch_down(touch)
            return True

class OptionToggle(FlatToggleButton):
    field_name = StringProperty('')
    field_value = NumericProperty(None)


class ToggleGroup(StackLayout):
    group_name = StringProperty('default')
    field_name = StringProperty('')
    font_group_id = StringProperty('default')
    field_data = DictProperty({})
    toggle_callback = ObjectProperty(None)
    current_value = NumericProperty(0)

    def on_field_data(self, instance, value):
        self.render()

    def update_render(self):
        toggle_layout = self.ids.toggle_layout
        app_root = self.app_root
        field_name = self.field_name
        emitter = app_root.emitter
        em_value = getattr(emitter, field_name)
        for widget in toggle_layout.children:
            if widget.field_value == em_value:
                widget.state = 'down'
            else:
                widget.state = 'normal'

    def render(self):
        toggle_layout = self.ids.toggle_layout
        for widget in toggle_layout.children:
            widget.font_ramp_tuple = ('default', '1')
        toggle_layout.clear_widgets()
        field_data = self.field_data
        options = field_data['choices']
        self.group_name = field_data['name']
        self.font_group_id = font_group_id = field_data['name']
        field_name = self.field_name
        callback = self.toggle_callback
        app_root = self.app_root
        emitter = app_root.emitter
        em_value = getattr(emitter, field_name)
        for option_name, value in options:
            new_toggle = OptionToggle(field_name=field_name, field_value=value,
                font_ramp_tuple=(font_group_id, '1'), no_up=True, 
                group=field_name, text=option_name)
            if value == em_value:
                new_toggle.state = 'down'
            toggle_layout.add_widget(new_toggle)
            if callback is not None:
                new_toggle.bind(state=callback)


class GamePanel(FloatLayout):
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            root = self.root
            touch.grab(self)
            current_entity = root.current_entity
            entity = root.gameworld.entities[current_entity]
            pos_comp = entity.position
            rot_comp = entity.rotate
            #last_pos = (pos_comp.x, pos_comp.y)
            pos_comp.x = touch.x
            pos_comp.y = touch.y
            # vec = Vector(pos_comp.x, pos_comp.y) - Vector(*last_pos)
            # rot_comp.r = degrees(atan2(vec[1], vec[0]))

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            root = self.root
            current_entity = root.current_entity
            entity = root.gameworld.entities[current_entity]
            pos_comp = entity.position
            rot_comp = entity.rotate
            #last_pos = (pos_comp.x, pos_comp.y)
            pos_comp.x = touch.x
            pos_comp.y = touch.y
            # vec = Vector(pos_comp.x, pos_comp.y) - Vector(*last_pos)
            # rot_comp.r = degrees(atan2(vec[1], vec[0]))

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)


class SliderGroup(StackLayout):
    group_name = StringProperty('default')
    field_name = StringProperty('')
    font_group_id = StringProperty('default')
    field_data = DictProperty({})
    slider_callback = ObjectProperty(None)

    def on_field_data(self, instance, value):
        self.render()

    def update_render(self):
        app_root = self.app_root
        emitter = app_root.emitter
        field_name = self.field_name
        count = self.field_data['count']
        value = getattr(emitter, field_name)
        slider_layout = self.ids.slider_layout
        slider_children = slider_layout.children[::-1]
        if count > 1:
            for index in range(count):
                slider = slider_children[index]
                slider.ids.value_slider.ids.slider.value = value[index]
        else:
            slider = slider_children[0]
            slider.ids.value_slider.ids.slider.value = value

    def render(self):
        slider_layout = self.ids.slider_layout
        for widget in slider_layout.children:
            widget.font_group_id = 'default'
        slider_layout.clear_widgets()
        field_data = self.field_data
        field_bounds = field_data['bounds']
        step = field_data['step']
        self.group_name = field_data['name']
        field_name = self.field_name
        self.font_group_id = font_group_id = field_data['name']
        count = field_data['count']
        callback = self.slider_callback
        app_root = self.app_root
        emitter = app_root.emitter
        value = getattr(emitter, field_name)
        if count > 1:
            for index, name in enumerate(field_data['value_names']):
                bounds = field_bounds[index]
                new_slider = NamedValueSlider(
                    minimum=bounds[0], maximum=bounds[1], step=step,
                    font_group_id=self.font_group_id, slider_name=name,
                    size_hint=(1., None), height=dp(50), field_count=count,
                    field_name=field_name, slider_group=self,
                    )
                slider_layout.add_widget(new_slider)
                new_slider.ids.value_slider.ids.slider.value = value[index]
                if callback is not None:
                    new_slider.bind(current_value=callback)
        else:
            bounds = field_bounds[0]
            new_slider = NamedValueSlider(
                    minimum=bounds[0], maximum=bounds[1], step=step,
                    font_group_id=self.font_group_id, slider_name='',
                    size_hint=(1., None), height=dp(50), field_count=count,
                    field_name=field_name, slider_group=self,
                    )
            slider_layout.add_widget(new_slider)
            new_slider.ids.value_slider.ids.slider.value = value
            if callback is not None:
                new_slider.bind(current_value=callback)


class ScrolledPopupContent(ScrollView):
    pass

class SavePopupContent(BoxLayout):
    save_callback = ObjectProperty(None)
    
    def filter_input(self, input_string, from_undo=False):
        return re.sub(r'\s+', '', input_string)

class TestGame(Widget):
    def __init__(self, **kwargs):
        super(TestGame, self).__init__(**kwargs)
        self.gameworld.init_gameworld(['position', 'scale', 'rotate',
            'color', 'particles', 'emitters', 'particle_renderer'],
            callback=self.init_game)
        self.emitter = None
        self.popup = None
        self.current_entity = None

    def init_game(self):
        self.setup_states()
        self.set_state()
        self.load_emitter()
        self.read_emitter_editor()

    def update_widgets(self):
        ui_panels = self.ids.editor_panel.ids.sm
        screens = ui_panels.screens
        for screen in screens:
            panel_layout = screen.ids.panel_layout
            for child in panel_layout.children:
                child.update_render()

    def read_emitter_editor(self):
        emitter_system = self.ids.emitter
        ui_panels = emitter_system.panels
        editor_fields = emitter_system.editor_fields
        sm = self.ids.editor_panel.ids.sm
        toggle_layout = self.ids.editor_panel.ids.screen_toggles
        panel_order = ui_panels['panel_order']
        for key in panel_order:
            panel_data = ui_panels[key]
            editor_screen = EditorScreen(name=key)
            for field_name in panel_data['fields']:
                field_data = editor_fields[field_name]
                field_type = field_data['type']
                if field_type == 'slider':
                    new_group = SliderGroup(size_hint=(1.0, None), 
                        slider_callback=self.update_emitter,
                        field_name=field_name)
                    new_group.bind(minimum_height=new_group.setter('height'))
                elif field_type == 'choice':
                    new_group = ToggleGroup(
                        toggle_callback=self.update_emitter_toggle,
                        field_name=field_name)
                editor_screen.ids.panel_layout.add_widget(new_group)
                new_group.field_data = field_data
            sm.add_widget(editor_screen)
            toggle_button = ScreenToggleButton(
                no_up=True, text=ui_panels[key]['name'],
                group='sm_buttons', screen_name=key)
            if key == 'general':
                toggle_button.state = 'down'
            toggle_button.bind(on_release=self.screen_toggle_callback)
            toggle_layout.add_widget(toggle_button)

    def screen_toggle_callback(self, instance):
        sm = self.ids.editor_panel.ids.sm
        sm.current = instance.screen_name

    def update_emitter_toggle(self, instance, value):
        if value == 'down':
            setattr(self.emitter, instance.field_name, instance.field_value)

    def update_emitter(self, instance, value):
        count = instance.field_count
        field_name = instance.field_name
        emitter = self.emitter
        if emitter is not None:
            if count == 1:
                setattr(emitter, field_name, value)
            else:
                widgets = instance.slider_group.ids.slider_layout.children[::-1]
                real_value = [wid.current_value for wid in widgets]
                setattr(emitter, field_name, real_value)

    def load_emitter(self):
        emitter_system = self.ids.emitter
        data = {'number_of_particles': 100, 'texture': 'particle', 
            'paused': False, 'speed': 50.}
        eff_id = emitter_system.load_effect_from_data(data, 'effect_test')
        comp_args = {
            'position': (200., 200.),
            'rotate': 0.,
            'emitters': ['effect_test'],
            }
        ent_id = self.gameworld.init_entity(
            comp_args, ['position', 'rotate', 'emitters'])
        self.current_entity = ent_id
        entity = self.gameworld.entities[ent_id]
        emitter_comp = entity.emitters
        for each in emitter_comp.emitters:
            if each is not None:
                self.emitter = each
                return

    def setup_states(self):
        self.gameworld.add_state(state_name='main', 
            systems_added=['particle_renderer'],
            systems_removed=[], systems_paused=[],
            systems_unpaused=['particle_renderer'],
            screenmanager_screen='main')

    def set_state(self):
        self.gameworld.state = 'main'

    def texture_choice_callback(self, instance):
        self.emitter.texture = instance.texture_name
        self.popup.dismiss()

    def open_texture_choice_popup(self):
        if self.popup is None:
            content = ScrolledPopupContent()
            content_layout = content.ids.content_layout
            self.popup = CustomPopup(content=content, title='Choose a Texture',
                title_size=sp(16))

            for texture_name in texture_manager.loaded_textures:
                wid = TextureChoiceButton(texture_name=texture_name,
                    texture=texture_manager.get_texture_by_name(texture_name),
                    on_release=self.texture_choice_callback,
                    font_group_id='texture_choice')
                content_layout.add_widget(wid)
        self.popup.open()

    def open_load_popup(self):
        effects_to_load = get_all_files(
            join(dirname(__file__), 'effects'), '.kep')
        content = ScrolledPopupContent()
        content_layout = content.ids.content_layout
        popup = CustomPopup(content=content, title='Load Effect',
            title_size=sp(16))
        emitter_system = self.ids.emitter
        loaded_effects = emitter_system.loaded_effects
        for effect in effects_to_load:
            real_effect_name = splitext(split(effect)[1])[0]
            if real_effect_name not in loaded_effects:
                emitter_system.load_effect(effect)
            wid = EffectChoiceButton(choice_name=real_effect_name,
                font_group_id='effect_choice',
                on_release=self.load_effect)
            wid.popup = popup
            content_layout.add_widget(wid)
        popup.open()
            
    def open_save_popup(self):
        content = SavePopupContent(save_callback=self.save_effect)
        popup = CustomPopup(content=content, title='Save Your Effect',
            title_size=sp(16))
        content.popup = popup
        popup.open()

    def load_effect(self, instance):
        emitter_system = self.ids.emitter
        emitter_system.copy_data_into_emitter(
            self.emitter, instance.choice_name)
        self.update_widgets()
        instance.popup.dismiss()

    def save_effect(self, instance):
        if instance.ids.text_input.text == '':
            return
        emitter_system = self.ids.emitter
        emitter_system.pickle_effect(
            self.emitter, join(dirname(__file__), 'effects', 
            instance.ids.text_input.text + '.kep'))
        instance.popup.dismiss()

class ParticlePandaApp(FlatApp):
    
    def build(self):
        self.setup_themes()
        self.setup_font_ramps()

    def setup_themes(self):
        variant_1 = {
            'FlatToggleButton':{
                'color_tuple': ('Purple', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'ripple_scale': 2.0,
                },
            'FlatButton':{
                'color_tuple': ('Purple', '500'),
                'ripple_color_tuple': ('Cyan', '900'),
                'font_color_tuple': ('Gray', '1000'),
                'ripple_scale': 2.0,
                },
            }

        variant_2 = {
            'FlatToggleButton':{
                'color_tuple': ('Cyan', '500'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '0000'),
                'font_ramp_tuple': ('Screen', '1'),
                'ripple_scale': 2.0,
                'multiline': True,
                },
            'FlatButton':{
                'color_tuple': ('Cyan', '800'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Cyan', '200'),
                'ripple_scale': 2.0,
                },
            }

        titles = {
            'FlatLabel':{
                'color_tuple': ('Gray', '1000'),
                },
            }

        subtitles = {
            'FlatLabel':{
                'color_tuple': ('Cyan', '900'),
                },
            }

        values = {
            'FlatLabel':{
                'color_tuple': ('Gray', '1000'),
                },
            'FlatButton':{
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '1000'),
                'ripple_scale': 2.0,
                },
            'FlatSlider': {
                'color_tuple': ('Cyan', '900'),
                'slider_color_tuple': ('Purple', '500'),
                'outline_color_tuple': ('Cyan', '100'),
                'slider_outline_color_tuple': ('Cyan', '100'),
                'ripple_color_tuple': ('Cyan', '100'),
                'ripple_scale': 10.,
                },
            'FlatToggleButton':{
                'color_tuple': ('Purple', '600'),
                'ripple_color_tuple': ('Cyan', '100'),
                'font_color_tuple': ('Gray', '0000'),
                'ripple_scale': 2.0,
                },
            }
        self.theme_manager.add_theme('pp', 'variant_1', variant_1)
        self.theme_manager.add_theme('pp', 'variant_2', variant_2)
        self.theme_manager.add_theme('pp', 'titles', titles)
        self.theme_manager.add_theme('pp', 'subtitles', subtitles)
        self.theme_manager.add_theme('pp', 'values', values)

    def setup_font_ramps(self):
        font_styles = {
            'Display 4': {
                'font': 'Roboto-Light.ttf', 
                'sizings': {'mobile': (112, 'sp'), 'desktop': (112, 'sp')},
                'alpha': .8,
                'wrap': False,
                }, 
            'Display 3': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (56, 'sp'), 'desktop': (56, 'sp')},
                'alpha': .8,
                'wrap': False,
                },
            'Display 2': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (45, 'sp'), 'desktop': (45, 'sp')},
                'alpha': .8,
                'wrap': True,
                'wrap_id': '1',
                'leading': (48, 'pt'),
                },
            'Display 1': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (34, 'sp'), 'desktop': (34, 'sp')},
                'alpha': .8,
                'wrap': True,
                'wrap_id': '2',
                'leading': (40, 'pt'),
                },
            'Headline': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (24, 'sp'), 'desktop': (24, 'sp')},
                'alpha': .9,
                'wrap': True,
                'wrap_id': '3',
                'leading': (32, 'pt'),
                },
            'Title': {
                'font': 'Roboto-Medium.ttf', 
                'sizings': {'mobile': (20, 'sp'), 'desktop': (20, 'sp')},
                'alpha': .9,
                'wrap': False,
                },
            'Subhead': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (16, 'sp'), 'desktop': (15, 'sp')},
                'alpha': .9,
                'wrap': True,
                'wrap_id': '4',
                'leading': (28, 'pt'),
                },
            'Body 2': {
                'font': 'Roboto-Medium.ttf', 
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .9,
                'wrap': True,
                'wrap_id': '5',
                'leading': (24, 'pt'),
                },
            'Body 1': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .9,
                'wrap': True,
                'wrap_id': '6',
                'leading': (20, 'pt'),
                },
            'Body 0': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (10, 'sp'), 'desktop': (9, 'sp')},
                'alpha': .9,
                'wrap': True,
                'wrap_id': '7',
                'leading': (20, 'pt'),
                },
            'Caption': {
                'font': 'Roboto-Regular.ttf', 
                'sizings': {'mobile': (12, 'sp'), 'desktop': (12, 'sp')},
                'alpha': .8,
                'wrap': False,
                },
            'Menu': {
                'font': 'Roboto-Medium.ttf', 
                'sizings': {'mobile': (14, 'sp'), 'desktop': (13, 'sp')},
                'alpha': .9,
                'wrap': False,
                },
            'Button': {
                'font': 'Roboto-Medium.ttf', 
                'sizings': {'mobile': (14, 'sp'), 'desktop': (14, 'sp')},
                'alpha': .9,
                'wrap': False,
                },
            }
        for each in font_styles:
            style = font_styles[each]
            sizings = style['sizings']
            style_manager.add_style(style['font'], each, sizings['mobile'], 
                sizings['desktop'], style['alpha'])

        style_manager.add_font_ramp('1', ['Display 2', 'Display 1', 
            'Headline', 'Subhead', 'Body 2', 'Body 1', 'Body 0',])


if __name__ == '__main__':
    ParticlePandaApp().run()
