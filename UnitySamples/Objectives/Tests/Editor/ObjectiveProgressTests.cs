using Greyhaven.Samples;
using NUnit.Framework;
using UnityEngine;

public sealed class ObjectiveProgressTests
{
    private GameObject owner;
    private ObjectiveProgress objective;

    [SetUp]
    public void SetUp()
    {
        owner = new GameObject("ObjectiveTest");
        objective = owner.AddComponent<ObjectiveProgress>();
    }

    [TearDown]
    public void TearDown()
    {
        Object.DestroyImmediate(owner);
    }

    [Test]
    public void FirstCompletionChangesStateAndInvokesEvent()
    {
        int count = 0;
        objective.Completed.AddListener(() => count++);

        Assert.That(objective.IsComplete, Is.False);
        Assert.That(objective.TryComplete(), Is.True);
        Assert.That(objective.IsComplete, Is.True);
        Assert.That(count, Is.EqualTo(1));
    }

    [Test]
    public void RepeatedCallsDoNotRepeatCompletion()
    {
        int count = 0;
        objective.Completed.AddListener(() => count++);

        objective.TryComplete();
        Assert.That(objective.TryComplete(), Is.False);
        Assert.That(count, Is.EqualTo(1));
    }

    [Test]
    public void DisabledObjectivesIgnoreCompletion()
    {
        objective.enabled = false;

        Assert.That(objective.TryComplete(), Is.False);
        Assert.That(objective.IsComplete, Is.False);
    }

    [Test]
    public void ResetAllowsCompletionAgain()
    {
        int count = 0;
        objective.Completed.AddListener(() => count++);

        objective.TryComplete();
        objective.ResetProgress();
        Assert.That(objective.IsComplete, Is.False);
        Assert.That(objective.TryComplete(), Is.True);
        Assert.That(count, Is.EqualTo(2));
    }

    [Test]
    public void CompletionCallbackCannotCompleteAgainWithoutReset()
    {
        bool repeatedResult = true;
        objective.Completed.AddListener(() => repeatedResult = objective.TryComplete());

        Assert.That(objective.TryComplete(), Is.True);
        Assert.That(repeatedResult, Is.False);
    }
}
