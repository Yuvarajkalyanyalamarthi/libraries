# 1. ENCAPSULATION & ABSTRACTION
class Vehicle:
    def __init__(self, make, model):     # ✅ Correct Constructor
        self._make = make               # Protected attribute (Encapsulation)
        self._model = model
        self.__engine_running = False   # Strongly private attribute

    def get_model(self):                # Encapsulation (getter)
        return self._model

    def start_engine(self):             # Abstraction (simple interface)
        if not self.__engine_running:
            self.__engine_running = True
            return f"Engine of {self._make} {self._model} started."
        return "Engine is already running."

    def drive(self):
        raise NotImplementedError("Subclasses must implement this method.")


# 2. INHERITANCE
class Car(Vehicle):
    def __init__(self, make, model, num_doors):
        super().__init__(make, model)   # Parent constructor call
        self.num_doors = num_doors

    # 3. POLYMORPHISM (overriding drive method)
    def drive(self):
        # Access private attribute using name mangling
        if self._Vehicle__engine_running:
            return f"The {self._make} {self._model} drives on 4 wheels."
        return f"Cannot drive {self._model}. Engine is off."

    def honk(self):
        return "Beep! Beep!"


# 4. POLYMORPHISM (same function works with different objects)
def operate_vehicle(vehicle):
    print(vehicle.start_engine())
    print(vehicle.drive())


# --- Usage ---
my_car = Car("Tesla", "Model S", 4)

print("--- My Car Operations ---")
print(my_car.honk())
print(f"Car Model: {my_car.get_model()}")   # Encapsulation

print("\n--- Polymorphism in Action ---")
operate_vehicle(my_car)
