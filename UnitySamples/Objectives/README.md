# Objective and trigger sample

Two small C# components for prototyping objectives in Unity:

- `ObjectiveProgress` stores completion state, invokes an Inspector-configurable event once, and can be reset.
- `ObjectiveTrigger` completes an assigned objective when a tagged actor or one of its child colliders enters a box trigger.

This is new sample code for future integration. It is separate from the existing game implementation and does not include scenes, movement controls, save data or game assets.

## Import into a Unity project

1. Copy this entire `Objectives` directory into the real project's `Assets/Samples/` directory.
2. Let Unity import the scripts and generate `.meta` files. Retain those generated files in source control.
3. Add `ObjectiveProgress` to a scene object.
4. Add `ObjectiveTrigger` to a separate object. Its required Box Collider should have **Is Trigger** enabled; configure the trigger size and assign the objective in the Inspector.
5. Use the built-in `Player` tag on the entering actor or a parent of its colliders. Any custom actor tag must already exist in the project's tag settings.
6. Ensure the colliders' layers can interact and that the trigger pair includes a Rigidbody. A test actor can use a kinematic Rigidbody with gravity disabled.
7. Add a callback to the objective's **Completed** event, such as enabling a UI object or invoking a scene-specific method.

An objective accepts completion only while its GameObject is active and its component is enabled. Disabling the component does not clear its state. Call `ResetProgress` explicitly to allow another completion; an actor already inside a trigger must exit and re-enter to produce a new entry event.

Completion state is in memory. The sample does not persist progress between scenes or sessions. It has no objective ordering rules or multiplayer authority checks.

## Validation

Five Edit Mode tests are included for first completion, repeated calls, disabled components, reset behavior and reentrant callbacks. With Unity Test Framework available in the destination project, open **Window → General → Test Runner**, select **EditMode** and run `ObjectiveProgressTests`.

The C# tests have not been executed here: this environment has no Unity Editor or C# compiler. Verify compilation and run the tests in the destination project before integration.

For a manual physics smoke check in Play Mode, move a test actor into the trigger, confirm one callback, then exit and re-enter to confirm the completed objective does not fire again. Reset the objective and repeat. Also try an untagged actor and a tagged parent with a child collider.

## API references

- [Unity trigger entry callbacks](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/MonoBehaviour.OnTriggerEnter.html)
- [Unity event invocation](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Events.UnityEvent.Invoke.html)
