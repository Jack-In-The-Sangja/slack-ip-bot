pipeline {
    agent any
    environment {
        SLACK_CHANNEL = credentials('jenkins-alert-channel')
        SLACK_CREDENTIAL_ID = 'slack-token'
    }
    stages {
        stage("Setup") {
            steps {
                script {
                    slackSend(
                        channel: SLACK_CHANNEL,
                        message: ":rocket: *[STARTED]* `${env.JOB_NAME}` #${env.BUILD_NUMBER}\n> Branch: `${env.GIT_BRANCH}`\n> Started by: `${env.BUILD_USER_ID ?: 'Unknown'}`",
                        tokenCredentialId: SLACK_CREDENTIAL_ID
                    )
                    if (env.GIT_BRANCH == "origin/main") {
                        target = "production"
                    } else if (env.GIT_BRANCH == "origin/develop") {
                        target = "development"
                    } else {
                        error ":bangbang: Unknown branch: ${env.GIT_BRANCH}"
                    }
                }
            }
        }

        stage("Copy Env Files") {
            steps {
                script {
                    echo "STAGE: Copy ${target == 'production' ? 'Prod' : 'Dev'} Env Files"
                    def configFileId = (target == "production")
                        ? '03645e0d-62e5-49bc-86c4-efcd075a983c'
                        : '065fbaa1-0641-41b8-98e9-f7fd3fb60419'
                    def envVarName = (target == "production") ? 'Prod_ENV' : 'Dev_ENV'

                    configFileProvider([
                        configFile(fileId: configFileId, variable: envVarName)
                    ]) {
                        sh """
                            cp \$$envVarName ${env.WORKSPACE}/.env
                        """
                    }
                }
            }
        }

        stage("Check SSH & Docker") {
            steps {
                echo "STAGE: Check SSH & Docker connection"
                script {
                    sh "docker ps -a"
                    sh "docker version"
                    sh "docker compose version || docker-compose version || echo 🚫 docker compose not found"
                }
            }
        }

        stage("Deploy") {
            steps {
                echo "STAGE: Deploy to ${target.toUpperCase()}"
                script {
                    def composeFile = (target == "production")
                        ? "docker-compose.prod.yml"
                        : "docker-compose.dev.yml"

                    sh "docker rm -f postgres || true"
                    sh "docker rm -f slack_ip_bot || true"
                    sh "docker compose -f ${composeFile} build"
                    sh "docker compose -f ${composeFile} up -d"
                }
            }
        }
    }

    post {
        success {
            slackSend(
                channel: SLACK_CHANNEL,
                message: ":white_check_mark: *[SUCCESS]* `${env.JOB_NAME}` #${env.BUILD_NUMBER}\n> :tada: Build completed successfully!\n> <${env.BUILD_URL}|View Build Details>",
                tokenCredentialId: SLACK_CREDENTIAL_ID
            )
        }
        failure {
            slackSend(
                channel: SLACK_CHANNEL,
                message: ":x: *[FAILED]* `${env.JOB_NAME}` #${env.BUILD_NUMBER}\n> :warning: Reason: `${currentBuild.description ?: 'Unknown - check console output'}`\n> <${env.BUILD_URL}|View Build Logs>",
                tokenCredentialId: SLACK_CREDENTIAL_ID
            )
        }
        always {
            slackSend(
                channel: SLACK_CHANNEL,
                message: ":bell: *[FINISHED]* `${env.JOB_NAME}` #${env.BUILD_NUMBER}\n> Status: *${currentBuild.currentResult}*\n> Time: `${new Date().format("yyyy-MM-dd HH:mm:ss", TimeZone.getTimeZone("Asia/Seoul"))}`\n> <${env.BUILD_URL}|Open Build>",
                tokenCredentialId: SLACK_CREDENTIAL_ID
            )
        }
    }
}
