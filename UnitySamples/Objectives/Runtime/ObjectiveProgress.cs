using UnityEngine;
using UnityEngine.Events;

namespace Greyhaven.Samples
{
    /// <summary>A resettable objective that invokes its completion event once.</summary>
    [DisallowMultipleComponent]
    public sealed class ObjectiveProgress : MonoBehaviour
    {
        [SerializeField] private UnityEvent completed = new UnityEvent();

        public bool IsComplete { get; private set; }
        public UnityEvent Completed => completed;

        /// <summary>Returns true only when this call completes an active objective.</summary>
        public bool TryComplete()
        {
            if (!isActiveAndEnabled || IsComplete)
            {
                return false;
            }

            // Commit state before callbacks, including callbacks that try again.
            IsComplete = true;
            completed.Invoke();
            return true;
        }

        public void ResetProgress()
        {
            IsComplete = false;
        }
    }
}
