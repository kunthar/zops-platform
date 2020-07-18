import {Component, OnInit} from '@angular/core';
import {NgForm} from "@angular/forms";
import {ForgotPasswordService} from "../../services/forgot-password.service";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: module.id,
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css']
})
export class ForgotPasswordComponent implements OnInit {

  loading = false;
  isSuccess = false;
  anyError = false;
  resetPasswordToken = "";
  isResetActive = false;

  constructor(private forgotPasswordService: ForgotPasswordService, private router: Router,
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
    t.route.queryParams.subscribe(params => {
      if (params['token'] != undefined) {
        t.isResetActive = true;
        t.resetPasswordToken = params['token'];
      }
    });
  }

  forgotPassword(forgotForm: NgForm) {
    this.loading = true;
    this.forgotPasswordService.forgotPassword(forgotForm.value.email).subscribe(
      res => {
        this.isSuccess = true;
      },
      error => {
        this.anyError = true;
        console.log(error);
      }
    );
    this.loading = false;
  }

  resetPassword(resetForm: NgForm) {
    this.loading = true;
    this.forgotPasswordService.resetPassword(resetForm.value.password, this.resetPasswordToken)
      .subscribe(
        res => {
          this.isSuccess = true;

          setTimeout(() => {
            this.router.navigate(['/signin'])
              .catch(error => {
                location.reload();
                console.log(error);
              });
          }, 5000);
        },
        error => {
          this.loading = false;
          this.anyError = true;
          console.log(error);
        }
      );
  }

}
