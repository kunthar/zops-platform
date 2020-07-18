import {Component, OnInit} from "@angular/core";
import {ServiceService} from "../../services/service.service";
import {ActivatedRoute, Router} from "@angular/router";
import {DefaultServiceInformation} from "../../models/DefaultServiceInformation";
import {NgForm} from "@angular/forms";
import {CreateServiceResponse} from "../../models/CreateServiceResponse";
import {ProjectService} from "../../services/project.service";
import {ServiceResponse} from "../../models/ServiceResponse";

@Component({
  selector: "app-service",
  templateUrl: "./service.component.html",
  styleUrls: ["./service.component.css"]
})
export class ServiceComponent implements OnInit {

  anyError = false;
  loading = false;
  projectId: string;
  serviceId: string;
  projectsServices;
  defaultServiceInfo = DefaultServiceInformation;
  data: any = {};

  constructor(private router: Router, private service: ServiceService,
              private projectService: ProjectService, private route: ActivatedRoute) {
    this.route.params.subscribe(params => {
      this.projectId = params["projectId"];
      this.serviceId = params["serviceId"];
    });
  }

  ngOnInit() {
    if (!this.defaultServiceInfo.map(s => s.codeName).includes(this.serviceId)) {
      this.router.navigate(["/notfound"])
        .catch(error => {
          location.reload();
          console.log(error);
        });
    }
    this.getService();
  }

  getProjectsServices(event) {
    this.projectsServices = event;
    this.defaultServiceInfo.map(s => {
      if (s.codeName == this.serviceId) {
        s.active = true;
      }
    });
  }

  createService(f: NgForm) {
    this.loading = true;
    this.service.sendCreateServiceRequest(this.projectId, this.serviceId, f.value.serviceName, f.value.serviceDesc)
      .subscribe(
        (res: CreateServiceResponse) => {
          location.reload();
        },
        error => {
          this.loading = false;
          this.anyError = true;
          console.log(error);
        }
      );
  }

  getService(){
    this.loading = true;
    this.service.getServiceData(this.projectId, this.serviceId)
      .subscribe(
        (res: ServiceResponse) => {
          this.data = res.content;
        },
        error => {
          this.loading = false;
          this.anyError = true;
          console.log(error);
        }
      );
  }

}
