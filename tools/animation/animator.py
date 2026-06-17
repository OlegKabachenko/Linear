__all__ = "Animator"

from collections import deque
from functools import partial
from kivy.animation import Animation


class Animator:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_p_widget_animation = False
        self.animation_queue = deque()

    def process_animation_queue(self):
        if self.animation_queue:
            next_animation = self.animation_queue.popleft()
            next_animation()
        else:
            self.is_p_widget_animation = False

    def set_widget_anim_status(self, widget, status: bool):
        if hasattr(widget, 'is_animated'):
            widget.is_animated = status

    def animate_widget_vertical(self, widget, f_opacity, f_height_mlt, anim_duration=0.5, on_complete_extra_action=None,
                                before_extra_action=None, is_from_queue=False):
        if self.is_p_widget_animation and not is_from_queue:
            self.animation_queue.append(
                lambda: self.animate_widget_vertical(widget, f_opacity, f_height_mlt, anim_duration,
                                                     on_complete_extra_action, before_extra_action, True))
            return

        self.is_p_widget_animation = True
        # If the widget needs this flag for internal logic
        self.set_widget_anim_status(widget, True)

        height = widget.height * f_height_mlt

        if before_extra_action:
            before_extra_action()

        animation = Animation(opacity=f_opacity, height=height, duration=anim_duration)
        on_complete_action = partial(self.on_animation_complete, on_complete_extra_action, widget)
        animation.bind(on_complete=on_complete_action)
        animation.start(widget)

    def on_animation_complete(self, on_complete_extra_action, widget, *args):
        self.set_widget_anim_status(widget, False)
        if on_complete_extra_action:
            on_complete_extra_action()
        self.process_animation_queue()

    def prepare_widget_for_add(self, widget):
        widget.height = 0
        widget.opacity = 0

    def animate_widget_add(self, container, widget, anim_duration=0.5, on_complete_extra_action=None,
                           is_from_queue=False):
        if self.is_p_widget_animation and not is_from_queue:
            self.animation_queue.append(
                lambda: self.animate_widget_add(container, widget, anim_duration, on_complete_extra_action, True))
            return

        container.add_widget(widget)
        # Force the on_size event to trigger, ensuring the widget adjusts its height properly for the upcoming animation.
        widget.height = widget.height + 1

        before_action = partial(self.prepare_widget_for_add, widget)
        self.animate_widget_vertical(widget, 1, 1, anim_duration, on_complete_extra_action, before_action,
                                     is_from_queue=is_from_queue)

    def animate_widget_delete(self, container, widget, anim_duration, is_from_queue=False):
        after_delete = partial(container.remove_widget, widget)
        self.animate_widget_vertical(widget, 0, 0, anim_duration, after_delete, is_from_queue=is_from_queue)

    def animate_container_clear(self, container, anim_duration=0.5, is_from_queue=False):
        if self.is_p_widget_animation and not is_from_queue:
            self.animation_queue.append(
                lambda: self.animate_container_clear(container, anim_duration, True))
            return

        if container.children:
            for i, widget in enumerate(container.children):
                if i == 0:
                    # The first widget is deleted immediately
                    self.animate_widget_delete(container, widget, anim_duration, is_from_queue=is_from_queue)
                else:
                    # For all other widgets, add their deletion animation to the start of the queue.
                    # This ensures that the first widget will be deleted first and subsequent widgets will follow immediately.
                    self.animation_queue.insert(0 + (i - 1),
                                                lambda: self.animate_widget_delete(container, widget, anim_duration,
                                                                                   is_from_queue=True))

        else:
            self.process_animation_queue()
