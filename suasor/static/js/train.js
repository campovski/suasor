// Accumulating grades string. It will be returned to Django via GET request.
var GRADES = "";

/*
  Removes content of previous person and loads content for new one.
  @param idx: index of next person to grade
  @param maxIdx: length of trainset
*/
function gradeNext(idx, maxIdx, grade) {
  // If idx = 0, this is when the page loads, meaning we do not have any
  // user to grade or remove any content.
  if (idx != 0) {
    // Add grade to GRADES.
    GRADES = GRADES + grade;

    // Remove previous person from sight.
    var previousPersonDiv = document.getElementById((idx-1).toString());
    previousPersonDiv.style.display = "none";
  }

  // Show next one.
  if (idx < maxIdx) {
    var newPersonDiv = document.getElementById(idx.toString());
    newPersonDiv.style.display = "inline-block";
  } else {
    var finishDiv = document.getElementById("finishBlock");
    finishDiv.style.display = "inline-block";
  }
}

/*
  Create GET request with userID and grades in URL for Django to
  process and save grades.
  @param userId: Facebook ID of user that graded
*/
function finishGrading(userId) {
  // Create relative URL for GET request.
  var url = userID + "?" + GRADES.toString();

  // Create GET request.
  var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send(null);
}
