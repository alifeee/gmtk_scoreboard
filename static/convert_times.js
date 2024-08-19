function timeSince(date) {
  var seconds = Math.floor((new Date() - date) / 1000);

  var interval = seconds / 31536000;

  if (interval > 2) {
    return Math.floor(interval) + " years";
  }
  interval = seconds / 2592000;
  if (interval > 2) {
    return Math.floor(interval) + " months";
  }
  interval = seconds / 86400;
  if (interval > 2) {
    return Math.floor(interval) + " days";
  }
  interval = seconds / 3600;
  if (interval > 2) {
    return Math.floor(interval) + " hours";
  }
  interval = seconds / 60;
  if (interval > 2) {
    return Math.floor(interval) + " minutes";
  }
  return Math.floor(seconds) + " seconds";
}

document.addEventListener("DOMContentLoaded", () => {
  console.log("convertimg times");
  timestamp_tds = document.querySelectorAll(".timestamp");
  timestamp_tds.forEach((td) => {
    let time_str = td.textContent;
    let timesince = timeSince(Date.parse(time_str));
    td.innerHTML = `<time datetime="${time_str}">${timesince} ago</time>`;
  });
});
