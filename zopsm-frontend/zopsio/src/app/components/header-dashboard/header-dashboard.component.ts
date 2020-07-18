import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {ProjectService} from "../../services/project.service";
import {RetrieveProjectResponse} from "../../models/RetrieveProjectResponse";
import {DefaultServiceInformation} from "../../models/DefaultServiceInformation";
import {ProjectListResponse} from "../../models/ProjectListResponse";
import {Router} from "@angular/router";

@Component({
  selector: 'app-header-dashboard',
  templateUrl: './header-dashboard.component.html',
  styleUrls: ['./header-dashboard.component.css']
})
export class HeaderDashboardComponent implements OnInit {

  @Input()
  projectId: string;

  @Input()
  serviceId: string;

  @Output()
  projectsServicesOut: EventEmitter<boolean[]> = new EventEmitter<boolean[]>();

  projectList: [any];
  projectsServices = [false];
  defaultProj: string;
  showServicesOnTab = true;
  codeNames = DefaultServiceInformation.map(s => s.codeName);
  names = DefaultServiceInformation.map(s => s.name);

  constructor(private projectService: ProjectService, private router: Router) {
  }

  ngOnInit() {
    this.getProjectsList();
    if (this.projectId != undefined) {
      if (this.projectId == "new-project") {
        this.defaultProj = "New Project";
        this.showServicesOnTab = false;
      } else {
        this.getSelectedProject(this.projectId);
      }
    } else {
      this.defaultProj = "All Projects";
      this.showServicesOnTab = false;
    }
  }

  getSelectedProject(id: string) {
    this.projectService.retrieveProject(id).subscribe(
      (res: RetrieveProjectResponse) => {
        this.defaultProj = res.content.name;
        for (let i = 0; i < this.codeNames.length; i++) {
          this.projectsServices[i] = res.content.services.includes(this.codeNames[i]);
        }
        this.projectsServicesOut.emit(this.projectsServices);
      },
      error => {
        console.log(error);
      }
    );
  }

  getProjectsList(): any {
    this.projectService.getProjects().subscribe(
      (res: ProjectListResponse) => {
        if (res.content.length != 0) {
          this.projectList = res.content;
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
}
