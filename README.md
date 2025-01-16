## Project Description

This application scrapes restaurant menus from UberEats, DoorDash, and GrubHub, converts them into AIO format, and integrates them into our system in under 15 minutes, streamlining the restaurant pre-onboarding process.

## Folder Structure

```
Online To AIO/
│
├── .streamlit/
│   └── config.toml
│
├── competitor/
│   └── online_to_aio.py
│
├── py/
├── resource/
│
├── utils/
│   └── missing_fields/
│       └── fill.py
│       └── frontend.py
│   └── logging_config.py
│   └── online_endpoint.py
│
├── .env               
├── .gitignore         
├── app.py             
├── docker-compose.yml 
├── Dockerfile         
├── README.md          
└── requirements.txt
```

## Installation & Setup

#### Local Host
```
pip install -r requirements.txt
streamlit run app.py
```

#### Docker Container
```
docker build -t online-to-aio .
docker run -p 8027:8027 online-to-aio
```