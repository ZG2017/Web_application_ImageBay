# Web_application_ImageBay
ImageBay web application using AWS cloud based on Flask framework
1. The whole web application is deployed on AWS. using modoules such as EC2, S3, DynamoDB.
2. User can signup/signin there own account. With in the account, user can view images and upload new images. All images are stored on S3.
3. The user information and storage information are saved on DynamoDB encoded.
4. The EC2 instance handle all the request. An load balancer is put on the web framework to create/destory the EC2 instances when traffic is too busy or too idle, respectively.
5. Also there is an Mananger EC2 instance used to track the traffic of website and all EC2 instances have been created. Manager can destory the instances manually or set the thredhold for load balancer.
