pipeline {
  agent any
  stages {
    stage('Configure') {
      steps {
        sh '''cp /var/lib/jenkins/postgres.env .'''
        echo 'Copied PostgreSQL and Django environment.'
        withCredentials([string(credentialsId: '	f8066a74-2a9c-4510-8bd5-7edb569fff14', variable: 'human1db'), string(credentialsId: '7650c2ee-c69d-4499-a180-b089acfd1afc', variable: 'yeast8db'), string(credentialsId: '	5013ec59-acd1-4b13-a0c2-90904f2aceb1', variable: 'gemsdb')]) {
          sh '''
            wget $human1db -O human1.db
            wget $gemsdb -O gems.db
            wget $yeast8db -O yeast8.db
          '''
        }
        echo 'Downloaded source databases.'
      }
    }
    stage('Build') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml build --build-arg NGINXCONF=nginx-dev.conf
        '''
        echo 'Built new Docker images.'
      }
    }
    stage('Cleanup running containers') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker rm $(docker ps -a -q) || true
          docker volume prune --force || true
        '''
        echo 'Stopped active Docker containers and deleted Docker volumes.'
      }
    }
    stage('Run') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d
        '''
        echo 'Running the new Docker images.'
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          docker exec -i db psql -U postgres < human1.db
          docker exec -i db psql -U postgres < yeast8.db
          docker exec -i db psql -U postgres < gems.db

          docker exec backend python manage.py makemigrations
          docker exec backend python manage.py migrate --database yeast8 --fake
          docker exec backend python manage.py migrate --database human1 --fake
          docker exec backend python manage.py migrate --database gems --fake
        '''
      }
    }
    stage('Clean up') {
      steps {
        sh '''
          docker rmi $(docker images -q) --force || true
          rm *.db
        '''
        echo 'Deleted old Docker images and containers. We are live!'
      }
    }
  }
}
