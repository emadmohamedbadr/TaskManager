from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from users.models import User
from .models import Task

class TaskViewsTests(TestCase):
    def setUp(self):
        """
        Set up test data before each test.
        """
        # Create a manager user
        self.manager = User.objects.create(
            first_name="Manager",
            last_name="User",
            email="manager@example.com",
            role="manager",
            password="managerpassword"  # Unhashed password (for testing purposes only)
        )

        # Create an employee user
        self.employee = User.objects.create(
            first_name="Employee",
            last_name="User",
            email="employee@example.com",
            role="employee",
            password="employeepassword"  # Unhashed password (for testing purposes only)
        )

        # Create a test task
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            assigned_to=self.employee,
            status="pending",
            priority="medium"
        )

        # Set up the test client
        self.client = Client()

    def _login_user(self, user):
        """
        Log in a user manually using sessions.
        """
        session = self.client.session
        session['user_id'] = user.id
        session['user_role'] = user.role
        session.save()

    def test_manager_tasks_view(self):
        """
        Test the manager tasks view.
        """
        # Log in as the manager
        self._login_user(self.manager)

        # Access the manager tasks page
        response = self.client.get(reverse('tasks:manager_tasks'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")  # Check that the task is displayed on the page

    def test_employee_tasks_view(self):
        """
        Test the employee tasks view.
        """
        # Log in as the employee
        self._login_user(self.employee)

        # Access the employee tasks page
        response = self.client.get(reverse('tasks:employee_tasks'))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Task")  # Check that the task is displayed on the page

    def test_add_task_view(self):
        """
        Test adding a new task (by the manager).
        """
        # Log in as the manager
        self._login_user(self.manager)

        # Data for the new task
        data = {
            'title': 'New Task',
            'description': 'This is a new task',
            'assigned_to': self.employee.id,
            'priority': 'high'
        }

        # Send a POST request to add the task
        response = self.client.post(reverse('tasks:add_task'), data)

        # Check that the task was added successfully
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertTrue(Task.objects.filter(title='New Task').exists())  # Check that the task exists in the database

    def test_update_task_status_view(self):
        """
        Test updating the task status (by the employee).
        """
        # Log in as the employee
        self._login_user(self.employee)

        # Data for the update
        data = {
            'status': 'completed'
        }

        # Send a POST request to update the task status
        response = self.client.post(reverse('tasks:update_task_status', args=[self.task.id]), data)

        # Check that the response is successful
        self.assertEqual(response.status_code, 302)  # Check for redirection

        # Refresh the task from the database
        self.task.refresh_from_db()

        # Check that the task status was updated
        self.assertEqual(self.task.status, 'completed')

    def test_delete_task_view(self):
        """
        Test deleting a task (by the manager).
        """
        # Log in as the manager
        self._login_user(self.manager)

        # Send a POST request to delete the task
        response = self.client.post(reverse('tasks:delete_task', args=[self.task.id]))

        # Check that the task was deleted successfully
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())  # Check that the task no longer exists in the database

    def test_logout_view(self):
        """
        Test logging out.
        """
        # Log in as the manager
        self._login_user(self.manager)

        # Access the logout page
        response = self.client.get(reverse('tasks:log_out'))

        # Check that the user was logged out successfully
        self.assertEqual(response.status_code, 302)  # Check for redirection to the login page
        self.assertNotIn('user_id', self.client.session)  # Check that the session was cleared

    def test_task_list_view_with_filters(self):
        """
        Test filtering tasks.
        """
        # Log in as the manager
        self._login_user(self.manager)

        # Test filtering completed tasks
        response = self.client.get(reverse('tasks:task_list', kwargs={'filter_type': 'completed'}))
        self.assertEqual(response.status_code, 200)

        # Test filtering delayed tasks
        response = self.client.get(reverse('tasks:task_list', kwargs={'filter_type': 'delayed'}))
        self.assertEqual(response.status_code, 200)

        # Test filtering in-progress tasks
        response = self.client.get(reverse('tasks:task_list', kwargs={'filter_type': 'in_progress'}))
        self.assertEqual(response.status_code, 200)

        # Test showing all tasks (no filter)
        response = self.client.get(reverse('tasks:task_list'))
        self.assertEqual(response.status_code, 200)