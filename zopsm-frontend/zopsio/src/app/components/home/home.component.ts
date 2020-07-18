import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {

  code1 = `
          sendLogoutRequest() {
            return this.http.options(this.config.apiUrl + '/session/logout')
              .subscribe(
                res => {
                  sessionStorage.removeItem('currentUserToken');
                  // TODO: do what should do token expired
                },
                error => {
                  console.log(error);
                });
          }  
          `
  code2 = `
          using System;
          using System.Collections.Generic;
          using System.Linq;
          using System.Text;
        
            namespace lesson2Example1
          {
            class Program
          {
            static void Main(string[] args)
          {
            int bigNumber = 430;
            byte smallNumber;
            checked
          {
            smallNumber = (byte)bigNumber;
          }
          Console.WriteLine(smallNumber);
          }
          }
          } 
          `
  code3 = `
          class Mapping:
          def __init__(self, iterable):
          self.items_list = []
          self.__update(iterable)
          def update(self, iterable):
          for item in iterable:
          self.items_list.append(item) `
  code4 = `
          sendLogoutRequest() {
            return this.http.options(this.config.apiUrl + '/session/logout')
              .subscribe(
                res => {
                  sessionStorage.removeItem('currentUserToken');
                  // TODO: do what should do token expired
                },
                error => {
                  console.log(error);
                });
          `
  code5 = `
      <?php
        $variable = "name";
        $literally = 'My $variable will not print!\\\\n';
      
        print($literally);
        print "<br />";
      
        $literally = "My $variable will print!\\\\n";
      
        print($literally);
      ?>
          `
  code6 = `
          # define a class
          class Box
             # constructor method
             def initialize(w,h)
                @width, @height = w, h
             end
          
             # accessor methods
             def printWidth
                @width
             end
          
             def printHeight
                @height
             end
          end
          `
}
