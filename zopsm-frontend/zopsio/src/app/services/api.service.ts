import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {AppConfig} from "../app.config";

@Injectable()
export class ApiService {

  constructor(private http: HttpClient, private config: AppConfig) { }

  getApiData(projectId: string){
    return this.http.get(this.config.apiUrl + "/projects/" + projectId + "/api");
  }

}
