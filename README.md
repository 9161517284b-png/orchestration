# Домашняя работа по теме Оркестрация с Apache Airflow

- Задание выполнено через github codespace
- Был создан файл docker-compose.yaml с настрйоками Airflow + PostgreSQL
- Далее контейнер был успешно запущен
- В БД PostgreSQL была создана структура данных под API ISS:
CREATE TABLE iss_position (
    timestamp TIMESTAMP PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT
);
-  Далее был создан файл iss_position_dag.py в папке dags
- Далее был запущен Dags через консоль командами: docker exec -it orchestration-airflow-webserver-1 bash
airflow dags unpause iss_position_dag
airflow dags trigger iss_position_dag
-  Сталкивалась с проблемами разрешений, что потребовало запуска доп команд:
sudo chown -R $(whoami):$(whoami) dags plugins
sudo chmod -R 777 dags plugins
- Работа была выполнена для проекта Международной Космической Станции
- По итогу работы в папке logs появились доп данные
- Для проверки наличия данных в БД тербовались следующие команды:
docker exec -it orchestration-postgres-1 psql -U airflow -d analytics
SELECT * FROM iss_position ORDER BY timestamp DESC LIMIT 10