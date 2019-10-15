(function() {
  angular.module('topbarapp', []).directive('scrollClass', function($window) {
    return {
      restrict: 'A',
      link: function(scope, element) {
        var current;
        current = $window.pageYOffset;
        angular.element($window).on('scroll', function() {
          var ref;
          if (($window.innerHeight + $window.pageYOffset) >= document.body.offsetHeight) {
            scope.scrolled = false;
          } else {
            scope.scrolled = (ref = this.pageYOffset > current) != null ? ref : {
              true: false
            };
          }
          current = this.pageYOffset;
          return scope.$apply();
        });
      }
    };
  });

}).call(this);

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiPGFub255bW91cz4iXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7RUFBQSxPQUFPLENBQUMsTUFBUixDQUFlLEtBQWYsRUFBc0IsRUFBdEIsQ0FFQSxDQUFDLFNBRkQsQ0FFVyxhQUZYLEVBRTBCLFFBQUEsQ0FBQyxPQUFELENBQUE7V0FDeEI7TUFBQSxRQUFBLEVBQVUsR0FBVjtNQUNBLElBQUEsRUFBTSxRQUFBLENBQUMsS0FBRCxFQUFRLE9BQVIsQ0FBQTtBQUNKLFlBQUE7UUFBQSxPQUFBLEdBQVUsT0FBTyxDQUFDO1FBQ2xCLE9BQU8sQ0FBQyxPQUFSLENBQWdCLE9BQWhCLENBQXdCLENBQUMsRUFBekIsQ0FBNEIsUUFBNUIsRUFBc0MsUUFBQSxDQUFBLENBQUE7QUFDcEMsY0FBQTtVQUFBLElBQUcsQ0FBQyxPQUFPLENBQUMsV0FBUixHQUFzQixPQUFPLENBQUMsV0FBL0IsQ0FBQSxJQUErQyxRQUFRLENBQUMsSUFBSSxDQUFDLFlBQWhFO1lBQ0UsS0FBSyxDQUFDLFFBQU4sR0FBaUIsTUFEbkI7V0FBQSxNQUFBO1lBR0UsS0FBSyxDQUFDLFFBQU4sc0RBQTBDO2NBQUEsSUFBQSxFQUFPO1lBQVAsRUFINUM7O1VBSUEsT0FBQSxHQUFVLElBQUMsQ0FBQTtpQkFDWCxLQUFLLENBQUMsTUFBTixDQUFBO1FBTm9DLENBQXRDO01BRkk7SUFETjtFQUR3QixDQUYxQjtBQUFBIiwic291cmNlc0NvbnRlbnQiOlsiYW5ndWxhci5tb2R1bGUgJ2FwcCcsIFtdXG5cbi5kaXJlY3RpdmUgJ3Njcm9sbENsYXNzJywgKCR3aW5kb3cpIC0+XG4gIHJlc3RyaWN0OiAnQSdcbiAgbGluazogKHNjb3BlLCBlbGVtZW50KSAtPlxuICAgIGN1cnJlbnQgPSAkd2luZG93LnBhZ2VZT2Zmc2V0XG4gICAgYW5ndWxhci5lbGVtZW50KCR3aW5kb3cpLm9uICdzY3JvbGwnLCAoKSAtPlxuICAgICAgaWYgKCR3aW5kb3cuaW5uZXJIZWlnaHQgKyAkd2luZG93LnBhZ2VZT2Zmc2V0KSA+PSBkb2N1bWVudC5ib2R5Lm9mZnNldEhlaWdodFxuICAgICAgICBzY29wZS5zY3JvbGxlZCA9IGZhbHNlXG4gICAgICBlbHNlXG4gICAgICAgIHNjb3BlLnNjcm9sbGVkID0gQHBhZ2VZT2Zmc2V0ID4gY3VycmVudCA/IHRydWUgOiBmYWxzZVxuICAgICAgY3VycmVudCA9IEBwYWdlWU9mZnNldFxuICAgICAgc2NvcGUuJGFwcGx5KClcbiAgICByZXR1cm5cbiJdfQ==
//# sourceURL=coffeescript
