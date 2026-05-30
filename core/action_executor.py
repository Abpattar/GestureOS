import platform as sys_platform


class ActionExecutor:
    def __init__(self, context_detector):
        self.context_detector = context_detector

        if sys_platform.system() == "Windows":
            from os_platform import windows as plat
        else:
            from os_platform import ubuntu as plat

        self._platform = plat
        print(f"[Executor] Platform: {sys_platform.system()}")

    def execute(self, gesture_name):
        if gesture_name in ("system_activate", "system_deactivate"):
            return

        context = self.context_detector.get_context()
        action  = self.context_detector.get_gesture_action(gesture_name, context)

        if action is None:
            print(f"[Executor] No mapping for '{gesture_name}' in '{context}'")
            return

        print(f"[Executor] {gesture_name} → {context} → {action}")
        self._platform.execute(action)