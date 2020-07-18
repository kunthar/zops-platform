import {Component, OnInit} from "@angular/core";
import {ActivatedRoute, Router} from "@angular/router";
import {NgForm} from "@angular/forms";
import {ProjectService} from "../../services/project.service";
import {ServiceService} from "../../services/service.service";
import {RetrieveProjectResponse} from "../../models/RetrieveProjectResponse";
import {ProjectListResponse} from "../../models/ProjectListResponse";
import {CreateProjectResponse} from "../../models/CreateProjectResponse";
import {CreateServiceResponse} from "../../models/CreateServiceResponse";
import {DefaultServiceInformation} from "../../models/DefaultServiceInformation";
import {AccountService} from "../../services/account.service";
import {ApiService} from "../../services/api.service";
import {APIResponse} from "../../models/APIResponse";

@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.component.html",
  styleUrls: ["./dashboard.component.css"],
})
export class DashboardComponent implements OnInit {

  defaultServiceInfo = DefaultServiceInformation;
  projectsList;
  anyError = false;
  loading = false;
  newProject = false;
  isProjectSelected = false;
  reachedProjectLimit = false;
  createProjectAndService = false;

  description: string;
  projectId: string;
  name: string;
  id: string;
  fcmApiKeys: string;
  services: [string];
  userLimit: number;
  userUsed: number;

  constructor(private router: Router, private createService: ServiceService,
              private projectService: ProjectService,
              private route: ActivatedRoute,
              private account: AccountService,
              private apiService: ApiService) {
    this.route.params.subscribe(params => {
      this.projectId = params["projectId"];
    });
  }

  ngOnInit() {
    if (this.projectId == undefined) {
      this.getProjectList();
    }
    else if (this.projectId == "new-project") {
      this.newProject = true;
    }
    else {
      this.getSelectedProject(this.projectId);
      this.getAPI();
    }
  }

  createProject(f: NgForm) {
    this.loading = true;
    this.projectService.sendCreateProjectRequest(f.value.projectName, f.value.projectDesc)
      .subscribe(
        (projRes: CreateProjectResponse) => {
          for (let i = 0; i < this.defaultServiceInfo.length; i++) {
            if (this.defaultServiceInfo[i].active) {
              this.createService.sendCreateServiceRequest(projRes.content.id, this.defaultServiceInfo[i].codeName,
                this.defaultServiceInfo[i].name, f.value.projectName + " - " + this.defaultServiceInfo[i].name)
                .subscribe(
                  (serviceRes: CreateServiceResponse) => {
                    //todo: do what to do with added services inside dashboard.

                    this.createProjectAndService = true;
                    location.reload();
                    this.router.navigate(["/dashboard/" + projRes.content.id])
                      .catch(error => {
                        location.reload();
                        console.log(error);
                      });
                  },
                  error => {
                    this.loading = false;
                    this.anyError = true;
                    // todo: call project delete. because of the errors of create services.
                    console.log(error);
                  });
            }
          }
        },
        error => {
          if (error.status == 402) {
            this.reachedProjectLimit = true;
          } else {
            this.anyError = true;
          }
          this.loading = false;
          console.log(error);
        }
      );

  }

  getProjectList() {
    this.projectService.getProjects().subscribe(
      (res: ProjectListResponse) => {
        if (res.content.length != 0) {
          this.projectsList = res.content;
        } else {
          this.router.navigate(["/dashboard/new-project"])
            .catch(error => {
              location.reload();
              console.log(error);
            });
        }
      },
      error => {
        console.log(error);
      }
    );
  }

  getSelectedProject(id: string): any {
    this.projectService.retrieveProject(id).subscribe(
      (res: RetrieveProjectResponse) => {
        this.isProjectSelected = true;
        this.name = res.content.name;
        this.description = res.content.description;
        this.id = res.content.id;
        this.services = res.content.services;
        this.userLimit = res.content.userLimit;
        this.userUsed = res.content.userUsed;
      },
      error => {
        console.log(error);
        this.router.navigate(["/notfound"])
          .catch(error => {
            location.reload();
            console.log(error);
          });
      }
    );
  }

  getAPI() {
    this.apiService.getApiData(this.projectId).subscribe(
      (res: APIResponse) => {
        this.fcmApiKeys = res.content.fcmApiKeys;
      }
    );
  }

  /* deleteAccount() {
     this.account.deleteAccount().subscribe(
       res => {
         sessionStorage.clear();
         localStorage.clear();
         this.router.navigate(["/"])
           .catch(error => {
             location.reload();
             console.log(error);
           });
         console.log(res);
       },
       error => {
         console.log(error);
       }
     );
   } */

}
