import {Injectable} from '@angular/core';
import {HttpEvent, HttpInterceptor, HttpHandler, HttpRequest} from '@angular/common/http';
import {Observable} from "rxjs/Observable";
//import * as crypto from 'crypto-js';
import {finalize, tap} from 'rxjs/operators';

/**
 * this class is between client and server you can manage requests and changes minor things.
 * for more details: https://angular.io/guide/http#intercepting-all-requests-or-responses
 */
@Injectable()
export class NoopInterceptor implements HttpInterceptor {

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    req = req.clone({headers: req.headers.set('Content-Type', 'application/json')});
    if (sessionStorage.getItem('currentUserToken')) {
      req = req.clone({
        headers: req.headers.set('Authorization', sessionStorage.getItem('currentUserToken')
        )
      });
    }

    // if (req.body) {
    //   let newBody = req.clone().body;
    //   if (req.body.password) {
    //     newBody.password = crypto.SHA256(req.body.password).toString(crypto.enc.Hex);
    //   }
    //   req = req.clone({body: newBody});
    // }
    let errorExist;
    return next.handle(req).pipe(
      tap(
        // Succeeds when there is a response; ignore other events
        event => {
        },
        // Operation failed; error is an HttpErrorResponse
        error => errorExist = error.status
      ), finalize(() => {
        if (errorExist == 401) {
          sessionStorage.clear();
          localStorage.clear();
          location.reload();
        }
      }));
  }
}
