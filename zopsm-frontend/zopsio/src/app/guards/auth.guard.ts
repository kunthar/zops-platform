import {Injectable} from '@angular/core';
import {CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot} from '@angular/router';
import {SigninService} from '../services/signin.service';

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(private user: SigninService) {
  }

  canActivate(next: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    return this.user.checkAuth();
  }

  canActivateChild(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) { // use for child routes and to avoid redundancy in routes
    return this.canActivate(route, state);
  }
}
