def group = "secops"
def service = "hello-flask"

pipeline {
  //checkout scm
  //agent { dockerfile true }
  agent any
  stages {
    stage("Build Image") {
      steps {
        script {
          def customImage = docker.build("${group}_${service}")
        }
      }
    }
  }
}
