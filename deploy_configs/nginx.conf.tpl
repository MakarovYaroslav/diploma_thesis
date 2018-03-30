worker_processes  1;

events {
    worker_connections  1024;
}

http{
    include mime.types;

    server {
        listen 80;
        server_name {{ HOST }};
        charset utf-8;
        client_max_body_size 75M;

        location / {
            uwsgi_pass  unix:/{{ PROJECT_PATH }}/{{ PROJECT_NAME }}/{{ PROJECT_NAME }}.sock;
            include     uwsgi_params;
        }
    }
}