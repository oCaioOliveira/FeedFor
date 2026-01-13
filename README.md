# Description

This project is an API designed to be integrated into educational systems related to questionnaire applications.

With the required configurations and access permissions, this API can receive information about tests taken by students and generate individual Formative Feedback, which is sent by email. This feedback includes details such as justifications for answers that differ from the answer key and indicates possible areas for improvement.

In addition, the API can store questionnaire data in its database, making it possible to request an Excel report that will be sent to the teacher responsible for the related subject.

# Execution

This video is a demonstration and tutorial on how to use the FeedFor project:
[![FeedFor Demo](https://img.youtube.com/vi/KL6FrNapAPk/0.jpg)](https://www.youtube.com/watch?v=KL6FrNapAPk)

# How to Run

To run the application, you must first configure the `.env` file at the root of the project:

```env
# EMAIL CREDENTIALS
EMAIL_HOST_USER=youremail@hotmail.com
EMAIL_HOST_PASSWORD=yourpassword
```

Above is an example of a `.env` file that stores the configuration for the email service credentials and the local database. The email service credentials are used to send emails containing students’ Formative Feedback or reports to teachers. The database settings are used during project initialization to identify the data storage service to be used. If a local setup is desired, the default settings can be copied and pasted. If the goal is to connect to an external service, such as a cloud database, you must retrieve the information from that service and fill in the fields correctly.

After configuring the application’s `.env` file, simply run the command `docker-compose up -d` to start the project. The `-d` flag is optional and prevents the terminal from being flooded with unnecessary logs (the minimum requirement is a machine that supports Docker).

When the application starts for the **first time**, some additional commands must be executed to configure the environment:

1. Run `docker exec -it feedfor_web_1 python manage.py migrate` to apply the database migrations.
2. Run `docker exec -it feedfor_web_1 python manage.py createsuperuser` to create a superuser in the database, allowing access to the Django admin panel.

**Attention:**

* The first execution will take a bit longer due to Docker image downloads; after that, startup will always be fast.
* Make sure to provide correct email credentials; otherwise, feedback emails will not be sent.
* To check whether emails are being sent through the application logs, access the logs of the `feedfor_celery_1` container using the command `docker logs feedfor_celery_1 -f`. The `-f` flag is optional and allows you to follow the logs in real time.
