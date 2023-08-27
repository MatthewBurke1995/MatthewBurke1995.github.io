---
date: 2023-08-27
categories:
  - Python
  - Cloud
  - Terraform
---

#AWS Lambda Project

As a follow up on my post about writing a bayesian model to predict score outcomes, this post will be about the steps to productionize the functionality. The final product is an endpoint that will give the percentage odds of a Win/Draw/Lose outcome for each match. The bayesian posteriors are updated every week and saved to S3, the actual endpoint is an AWS lambda that pulls the posteriors from AWS.


The sequence diagram is as shown below. Let's run through the process of building up the Fargate and the Lambda services seperately.

``` mermaid
sequenceDiagram
  autonumber

  loop Weekly ETL
      Fargate->>Fargate: Weekly generate posteriors
      Fargate->>S3: Save posteriors
  end

  Loop User Request
      User->> Lambda: Request match probabilities
      Lambda->>S3: Pull posteriors
      Lambda->>Lambda: Simulate 100 games
      Lambda->>User: Send simulation results
  end
```

You can see the [github repo](https://github.com/MatthewBurke1995/Chalice-application) to build the seperate Lambda and Fargate components. The S3 bucket and ECR instances are external dependencies that should be built outside of terraform. 


## AWS Chalice: Lambda as a Backend

AWS Lambda is a 'Function as a Service'. Each time a call is made to a lambda instance the program is initialized, run once and then closed. Languages with high startup or shutdown costs are not appropriate for a lambda infrastructure which makes Python a good choice, although AWS Lambda does offer Java runtimes. There is no state that can be shared between executions with Lambda, any state will have to be saved to an external service such as S3 or DynamoDB.

When looking at what my options were for deploying python functions in Lambda I came across ['AWS Chalice'](https://aws.github.io/chalice/index.html), which is a library for writing endpoints or CRON jobs with a Flask like syntax. Chalice will handle the creation of the API Gateway, IAM roles and Cloudwatch events for scheduling.

You can see the Lambda function I created with Chalice to make those game predictions in [github](https://github.com/MatthewBurke1995/Chalice-application/blob/main/app/app.py#L32). The business logic and configuration for deployment is very brief thanks to the Chalice abstractions. But the abstractions are not perfect. During the deployment phase there is a static analysis of which services are used and what permissions need to be provided to the Lambda role. Unfortunately it missed my usage of the s3, to help out the static analysis I added a branch of code that uses S3 from the index function. When that was added then everything was deployed as expected.

## AWS Fargate

The function to calculate the bayesian posteriors had a dependency with the 'numpyro' and 'jax' libraries which exceeded the 150mb runtime limit of Lambda. When AWS Lambda is not fit for purpose but you still require a serverless solution then AWS Fargate can run containers on demand. You can see the code I used to set up the [Fargate weekly ETL on github](https://github.com/MatthewBurke1995/Chalice-application/tree/main/calculation). The process for creating your ECR repository and adding the docker image is done outside of Terraform, and arguably should be kept outside of Terraform. The configuration includes running the task on a weekly schedule with the proper S3 writes.

One of the issues I had when writing the terraform configuration was distinguishing between the execution role and the task role of the Fargate resource. Every Fargate instance should have a task_role_arn but Terraform can't pick this up at any point since the same "aws_ecs_task_definition" can be used with EC2 which wouldn't require the task_role_arn key. In brief the execution role should have enough permissions so start the Docker Container and the task role needs to have permissions to execute the code contained in the image e.g. "s3:PutObject" for writing to S3.

## Testing out the results

Currently (2023 August) there are only 3 gameweeks to base the data off and posterior values are likely to be all over the place, but we can still make predictions based on what we have seen. Use the 3 letter name for each team e.g. MCI, LIV, ARS, TOT, CHE, MUN, NEW, AVL.

<input placeholder="MCI" id="home" type="text">
<input placeholder="LIV" id="away" type="text">
<input class="md-button" type="submit" id="submitbutton">
<div id="results"></div>
<script>
  function updateValue(event) {
    var home = document.getElementById('home').value;

    var away = document.getElementById('away').value;

    fetch(`https://viwmsn8uyd.execute-api.us-east-2.amazonaws.com/api/match/${home}/${away}`, {
      method: "GET",
    })
    .then(r => r.json())
    .then(
      r => {
        var str = JSON.stringify(r['response']); //
        results.innerHTML = str;
      }
    )

  }

  submitbutton.addEventListener('click', updateValue);
</script>
