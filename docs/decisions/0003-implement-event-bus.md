# 3. Implement an Event Bus for Engine-Renderer Communication

* **Status:** Accepted
* **Context:** A direct link between the game engine and the renderer would violate our core principle of separation.
* **Decision:** Implement a simple publish/subscribe event bus. The engine publishes game events without knowledge of the subscriber.
* **Consequences:** The engine remains pure and testable in isolation. The renderer can be completely replaced without any changes to the engine logic.
