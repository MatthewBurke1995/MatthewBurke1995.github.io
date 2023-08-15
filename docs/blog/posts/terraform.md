---
date: 2023-07-31
categories:
  - Terraform
  - DevOps
---


# Terraform

My job title has never been 'DevOps' which is probably a good thing since having a dedicated DevOps team is arguably an antipattern. Throughout my career I've tended to work in smaller teams that are branched out from the core business, in which case I have had to deal with operations as I go.

Terraform seems to have reached a Docker level of industry awareness, so i've been catching up on the trend. 

As a way of giving myself a target I came across a devops takehome test on reddit. You can see [my solution on github](https://github.com/MatthewBurke1995/Dev-Ops-Take-Home). As for the take home questions:

Q: What is the rationale behind technology choices?
A: Github CICD, Docker and Terraform tend to be the common tools for their respective functionality which makes them the easiest to troubleshoot and find related documentation for any problems that occur.

Q: Any improvements you would make with more time?
A: I'd modularize the terraform code so I could make 1 for 1 replication of dev and prod without copy pasting code. If it needed to be public facing I'd buy a domain name and set up dns using terraform (probably through Route53 or Cloudflare). And then I'd run health check tests against the IP address, if unsuccessful I'd roll things back.

The app works, each push to master creates a docker image which would get deployed if I ran the `terraform apply` command but currently I'm only running `terraform plan` as the last step of the pipeline. 

Overall terraform is a much nicer experience than procedural coding using the AWS CLI or SDK.


