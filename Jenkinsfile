pipeline {
  agent any
  stages {
    stage('Docker cleanup') {
      steps {
        sh '''
          docker stop $(docker ps -a -q) || true
          docker rm $(docker ps -a -q) || true
          docker rmi $(docker images -q) || true
          docker volume prune --force || true
        '''
        echo 'Deleted all Docker containers and images.'
      }
    }
    stage('Configure') {
      steps {
        sh '''cp /var/lib/jenkins/postgres.env .'''
        echo 'Copied PostgreSQL and Django environment.'
      }
    }
    stage('Test') {
      steps {
        echo 'Should do some testing..'
      }
    }
    stage('Build') {
      steps {
        sh '''
          PATH=$PATH:/usr/local/bin
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml build
          docker-compose -f docker-compose.yml -f docker-compose-prod.yml up -d
        '''
      }
    }
    stage('Import databases') {
      steps {
        sh '''
          wget https://chalmersuniversity.box.com/shared/static/ux9bnfyycig8qgxtayjnjnczqt7b92b7.db -O human1.db
          wget https://chalmersuniversity.box.com/shared/static/om86nb6y8ji044wzoiljm8aghmbdvs41.db -O gems.db
          wget https://chalmersuniversity.box.com/shared/static/n3izn3hkp1hmmgodpxaczpkqd0p64ngf.db -O yeast8.db

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
          rm *.db
        '''
        echo 'We are live!'
      }
    }
  }
}
