class Tank:
    def __init__(self, analytics, hp=1000, shield=False):
        self.hp = hp
        self.shield = shield
        self.is_destroyed = False
        self.analytics = analytics

    def take_damage(self, damage):
        if self.shield:
            damage *= 0.5

        self.hp = max(0, self.hp - damage)

        if self.hp == 0:
            self.is_destroyed = True

            try:
                self.analytics.send_event("tank_destroyed")
            except TimeoutError:
                pass