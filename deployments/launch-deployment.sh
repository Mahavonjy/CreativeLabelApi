#!/usr/bin/env bash

kubectl apply -f elasticsearch-deployment.yaml
kubectl apply -f creative-db-deployment.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f app-ingress.yaml
