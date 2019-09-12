#!/usr/bin/env groovy
/*
 * Jenkinsfile for AstroFaker
 *
 *
 * Required Plug-ins
 * -----------------
 * - Warnings Next Generation
 * - Slack Notification
 *
 *
 * Required Shared Libraries
 * -------------------------
 * - dragons_ci
 *
 *
 * by Bruno C. Quint
 *
 */

 @Library('dragons_ci@master') _


 pipeline {

    agent any

    triggers {
        pollSCM('H * * * *')
    }

    options {
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        PATH = "$JENKINS_HOME/anaconda3/bin:$PATH"
        CONDA_ENV_NAME="astrofaker"
        CONDA_ENV_FILE="conda_env.yml"
    }

    stages {

        stage('Prepare') {
            steps {
                echo "Hello World"
            }
        }

    }



 }
