import {Component} from '@angular/core';
import {SignupService} from '../../services/signup.service';
import {Router} from "@angular/router";
import {Account} from "../../models/Account";

@Component({
  moduleId: module.id,
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {

  loading = false;
  isApproveSent = false;
  signUpModel = new Account();
  ToSFlag = false;
  announcementFlag = false;
  isConflict = false;
  anyError = false;
  terms = "deneme deneme deneme";

  constructor(private router: Router, private signupService: SignupService) {
    if (sessionStorage.getItem('currentUserToken')) {
      this.router.navigate(['/dashboard'])
        .catch(error => {
          location.reload();
          console.log(error);
        });
    }
  }

  startSignUp() {
    this.loading = true;
    this.signupService.signUp(this.signUpModel).subscribe(
      res => {
        this.isApproveSent = true;

        setTimeout(() => {
          this.router.navigate(['/'])
            .catch(error => {
              location.reload();
              console.log(error);
            });
        }, 5000);
      },
      error => {
        if (error.status == 409) {
          this.isConflict = true;
        } else {
          this.anyError = true;
        }
        console.log(error);
        this.loading = false;
      });
  }

}
