import {Component, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {AccountApprove} from "../../models/AccountApprove";
import {SignupApproveService} from "../../services/signup-approve.service";
import {AccountApproveResponse} from "../../models/AccountApproveResponse";

@Component({
  moduleId: module.id,
  templateUrl: './signup-approve.component.html',
  styleUrls: ['./signup-approve.component.css']
})
export class SignupApproveComponent implements OnInit {

  loading = false;
  //isSuccess = false;
  anyError = false;
  notExistOrConflict = false;
  approveModel = new AccountApprove();


  constructor(private router: Router, private signupApproveService: SignupApproveService,
              private route: ActivatedRoute) {
    if (sessionStorage.getItem('currentUserToken')) {
      this.router.navigate(['/dashboard'])
        .catch(error => {
          location.reload();
          console.log(error);
        });
    }
  }

  ngOnInit() {
    const t = this;
    let urlWithEscapeChars = "";
    t.route.queryParams.subscribe(params => {
      if (params['registrationId'] == undefined || params['approveCode'] == undefined || params['email'] == undefined) {
        this.router.navigate(['/'])
          .catch(error => {
            location.reload();
            console.log(error);
          });
      }

      urlWithEscapeChars = encodeURIComponent(t.router.url); // this is url with escape chars view.

      t.approveModel.registrationId = params['registrationId'];
      t.approveModel.approveCode = params['approveCode'];
      t.approveModel.email = params['email'];
    });
  }

  startSignUpApprove() {
    this.loading = true;
    this.signupApproveService.signUpApprove(this.approveModel)
      .subscribe((res: AccountApproveResponse) => {
          //this.isSuccess = true;
          sessionStorage.setItem('currentUserToken', res.content.token);
          this.router.navigate(['/dashboard'])
            .catch(error => {
              location.reload();
              console.log(error);
            });
        },
        error => {
          if (error.status == 404) {
            this.notExistOrConflict = true;
          } else {
            this.anyError = true;
          }
          console.log(error);
          this.loading = false;
        });
  }
}
