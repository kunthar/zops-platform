import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Router} from "@angular/router";
import {AppConfig} from "../app.config";
import 'rxjs/add/operator/toPromise';

@Injectable()
export class ProjectService {

  constructor(private http: HttpClient, private config: AppConfig, private router: Router) {
  }

  sendCreateProjectRequest(projectName: string, projectDesc: string) {
    return this.http.post(this.config.apiUrl + "/projects", {name: projectName, description: projectDesc});
  }

  getProjects() {
    return this.http.get(this.config.apiUrl + "/projects");
  }

  retrieveProject(projectId: string) {
    return this.http.get(this.config.apiUrl + "/projects/" + projectId);
  }
}
