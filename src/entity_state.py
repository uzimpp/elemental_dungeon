class EntityState:
    """Base class for all entity states"""
    def __init__(self, entity):
        self.entity = entity
        self.state_name = "base"
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass
    
    def update(self, dt, **kwargs):
        """Update logic for this state"""
        pass
    
    def handle_input(self, **kwargs):
        """Handle input while in this state"""
        return None  # Return next state if needed


class IdleState(EntityState):
    """Idle state for entities"""
    def __init__(self, entity):
        super().__init__(entity)
        self.state_name = "idle"
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('idle', force_reset=True)
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            # Determine facing direction from kwargs if available
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)


class WalkState(EntityState):
    """Walking state for entities"""
    def __init__(self, entity):
        super().__init__(entity)
        self.state_name = "walk"
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('walk', force_reset=True)
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)


class SprintState(EntityState):
    """Sprinting state for entities"""
    def __init__(self, entity):
        super().__init__(entity)
        self.state_name = "sprint"
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('sprint', force_reset=True)
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)


class CastState(EntityState):
    """Casting/attack state for entities"""
    def __init__(self, entity, duration=0.5):
        super().__init__(entity)
        self.state_name = "cast"
        self.timer = duration
        self.duration = duration
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('cast', force_reset=True)
        self.timer = self.duration
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)
        
        self.timer -= dt
        if self.timer <= 0:
            return IdleState(self.entity)
        return None


class SlashState(EntityState):
    """Slash/sweep attack state for entities"""
    def __init__(self, entity, duration=0.4):
        super().__init__(entity)
        self.state_name = "sweep"
        self.timer = duration
        self.duration = duration
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('sweep', force_reset=True)
        self.timer = self.duration
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)
        
        self.timer -= dt
        if self.timer <= 0:
            return IdleState(self.entity)
        return None


class HurtState(EntityState):
    """Hurt/damaged state for entities"""
    def __init__(self, entity, duration=0.3):
        super().__init__(entity)
        self.state_name = "hurt"
        self.timer = duration
        self.duration = duration
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('hurt', force_reset=True)
        self.timer = self.duration
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            dx = kwargs.get('dx', self.entity.dx if hasattr(self.entity, 'dx') else 0)
            dy = kwargs.get('dy', self.entity.dy if hasattr(self.entity, 'dy') else 0)
            self.entity.animation.update(dt, dx, dy)
        
        self.timer -= dt
        if self.timer <= 0:
            # If health is 0, transition to dying
            if hasattr(self.entity, 'health') and self.entity.health <= 0:
                return DyingState(self.entity)
            return IdleState(self.entity)
        return None


class DyingState(EntityState):
    """Dying state for entities"""
    def __init__(self, entity, duration=0.8):
        super().__init__(entity)
        self.state_name = "dying"
        self.timer = duration
        self.duration = duration
    
    def enter(self):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.set_state('dying', force_reset=True)
            # Calculate duration based on animation
            if hasattr(self.entity.animation, 'config') and 'dying' in self.entity.animation.config:
                animations_length = len(self.entity.animation.config['dying']['animations'])
                death_duration = self.entity.animation.config['dying']['duration'] * animations_length
                self.timer = death_duration
                self.duration = death_duration
    
    def update(self, dt, **kwargs):
        if hasattr(self.entity, 'animation') and self.entity.animation:
            self.entity.animation.update(dt)
        
        self.timer -= dt
        if self.timer <= 0:
            self.entity.alive = False
        return None  # Stay in dying state until the entity is destroyed


class NoAnimationState(EntityState):
    """State for entities without animations (like projectiles)"""
    def __init__(self, entity):
        super().__init__(entity)
        self.state_name = "none"
    
    def update(self, dt, **kwargs):
        # Do nothing for animation, entity update logic should handle movement
        pass


class EntityStateMachine:
    """State machine for entities"""
    def __init__(self, entity):
        self.entity = entity
        self.current_state = IdleState(entity)
        self.current_state.enter()
        
        # Map of state names to state classes for easy state switching
        self.states = {
            "idle": IdleState,
            "walk": WalkState,
            "sprint": SprintState,
            "cast": CastState,
            "sweep": SlashState,
            "hurt": HurtState, 
            "dying": DyingState,
            "none": NoAnimationState
        }
    
    def change_state(self, state_name, **kwargs):
        """Change to a new state by name"""
        if state_name in self.states:
            self.current_state.exit()
            # Instantiate with kwargs if needed
            duration = kwargs.get('duration', None)
            if duration is not None and state_name in ["cast", "sweep", "hurt", "dying"]:
                self.current_state = self.states[state_name](self.entity, duration)
            else:
                self.current_state = self.states[state_name](self.entity)
            self.current_state.enter()
            return True
        return False
    
    def update(self, dt, **kwargs):
        """Update the current state"""
        next_state = self.current_state.update(dt, **kwargs)
        if next_state:
            self.current_state.exit()
            self.current_state = next_state
            self.current_state.enter()
    
    def get_state_name(self):
        """Get the name of the current state"""
        return self.current_state.state_name 
