import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {SigninService} from '../../services/signin.service';
import {SigninResponse} from "../../models/SigninResponse";
import {NgForm} from "@angular/forms";

@Component({
  moduleId: module.id,
  templateUrl: './signin.component.html',
  styleUrls: ['./signin.component.css']
})
export class SigninComponent implements OnInit {

  loading = false;
  anyError = false;
  notfound = false;

  constructor(private router: Router, private user: SigninService) {
    if (sessionStorage.getItem('currentUserToken')) {
      this.router.navigate(['/dashboard'])
        .catch(error => {
          location.reload();
          console.log(error);
        });
    }
  }

  ngOnInit() {
  }

  startSignIn(f: NgForm) {
    const t = this;
    t.loading = true;
    t.user.sendSigninRequest(f.value.email, f.value.password)
      .subscribe(
        (res: SigninResponse) => {
          sessionStorage.setItem('currentUserToken', res.content.token);

          const url = '/dashboard';
          t.router.navigate([url])
            .catch(error => {
              location.reload();
              console.log(error);
            });
        },
        error => {
          if(error.status == 404){
            t.notfound = true;
          }
          else {
            t.anyError = true;
          }
          t.loading = false;
          console.log(error);
        });
  }
}
