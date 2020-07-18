import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {AppConfig} from "../app.config";

@Injectable()
export class ServiceService {

  constructor(private http: HttpClient, private config: AppConfig) {
  }

  sendCreateServiceRequest(projectId: string, codeName: string, serviceName: string, serviceDesc: string) {
    return this.http.post(this.config.apiUrl + "/projects/" + projectId + "/services", {
      serviceCatalogCode: codeName,
      name: serviceName,
      description: serviceDesc
    });
  }

  getServiceData(projectId: string, serviceCatalogCode: string){
    return this.http.get(this.config.apiUrl + "/projects/" + projectId + "/services/" + serviceCatalogCode);
  }

  deleteService(projectId: string, serviceCatalogCode: string){
    return this.http.delete(this.config.apiUrl + "/projects/" + projectId + "/services/" + serviceCatalogCode);
  }

}
