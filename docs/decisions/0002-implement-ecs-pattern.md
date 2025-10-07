# 2. Implement an Entity-Component-System (ECS) Pattern

* **Status:** Accepted
* **Context:** Game state management with traditional object-oriented hierarchies can become rigid and difficult to extend.
* **Decision:** Adopt the ECS pattern using the `esper` library to promote composition over inheritance.
* **Consequences:** All game objects will be entities composed of data-only components. All logic will be in systems, leading to a highly modular and flexible architecture.
