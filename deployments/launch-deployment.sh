#!/usr/bin/env bash

kubectl apply -f elasticsearch.yaml
kubectl apply -f creative-db.yaml
kubectl apply -f api.yaml
