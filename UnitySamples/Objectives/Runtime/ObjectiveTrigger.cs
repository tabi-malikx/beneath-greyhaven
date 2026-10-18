using UnityEngine;

namespace Greyhaven.Samples
{
    /// <summary>Completes an assigned objective when a tagged actor enters a box trigger.</summary>
    [DisallowMultipleComponent]
    [RequireComponent(typeof(BoxCollider))]
    public sealed class ObjectiveTrigger : MonoBehaviour
    {
        [SerializeField] private ObjectiveProgress objective;
        [SerializeField] private string actorTag = "Player";

        private void Reset()
        {
            GetComponent<BoxCollider>().isTrigger = true;
        }

        private void OnTriggerEnter(Collider other)
        {
            if (!isActiveAndEnabled || objective == null || string.IsNullOrWhiteSpace(actorTag))
            {
                return;
            }

            // A player's child colliders can share the tag on a parent actor.
            for (Transform actor = other.transform; actor != null; actor = actor.parent)
            {
                if (actor.CompareTag(actorTag))
                {
                    objective.TryComplete();
                    return;
                }
            }
        }
    }
}
