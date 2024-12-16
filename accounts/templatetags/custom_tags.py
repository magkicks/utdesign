from django import template

register = template.Library()

@register.simple_tag
def get_task_submission(task, task_submissions):
    """
    Returns the first submission for the given task, or None if no submission exists.
    """
    for submission in task_submissions:
        if submission.task.id == task.id:
            return submission
    return None
