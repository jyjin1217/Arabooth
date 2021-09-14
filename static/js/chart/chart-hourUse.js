
const hourUseChart = async (year, month) => {

  const uriOrign = "https://a3df8nbpa2.execute-api.ap-northeast-2.amazonaws.com/v1/log" + "?year=" + year + "&month=" + month;
  let response = await fetch(uriOrign, {method:'GET'})
  
  if(response.ok){
    let resJson = await response.json();

    let labelArr = ["10분 이하", "30분 이하", "1시간 이하", "2시간 이하", "초과 사용"];
    let dataArr = [0, 0, 0, 0, 0];      

    for(let key in resJson) {
        let boothName = resJson[key]['BoothName'];
        if (boothName == '테스트') continue;

        let duration = resJson[key]['Duration-sec'];
        if (duration == 'progressing') continue;
        
        let minute = duration / 60;
        let index = 4;
        if(minute <= 10) index = 0;
        else if (minute <= 30) index = 1;
        else if (minute <= 60) index = 2;
        else if (minute <= 120) index = 3;

        dataArr[index] += 1;
    }

    let maxY = 0;
    for(let i = 0; i < dataArr.length; i++){
      if(dataArr[i] > maxY) maxY = dataArr[i];
    }
    maxY = maxY - (maxY % 10) + 10;        


    let chartParent = document.getElementById("myBarChart");
    while (chartParent.firstChild){
      chartParent.removeChild(chartParent.firstChild);
    }
    let newCanvas = document.createElement('canvas');
    chartParent.appendChild(newCanvas);

    new Chart(newCanvas, {
      type: 'bar',
      data: {
        labels: labelArr,
        datasets: [{
          label: "사용자",
          backgroundColor: "#4e73df",
          hoverBackgroundColor: "#2e59d9",
          borderColor: "#4e73df",
          data: dataArr,
          maxBarThickness: 25,
        }],
      },
      options: {
        maintainAspectRatio: false,
        layout: {
          padding: {
            left: 10,
            right: 25,
            top: 25,
            bottom: 0
          }
        },
        scales: {
          xAxes: [{
            time: {
              unit: 'month'
            },
            gridLines: {
              display: false,
              drawBorder: false
            },
            ticks: {
              maxTicksLimit: 6
            }              
          }],
          yAxes: [{
            ticks: {
              min: 0,
              max: maxY,
              maxTicksLimit: 5,
              padding: 10,
              // Include a dollar sign in the ticks
              callback: function(value, index, values) {
                return number_format(value);
              }
            },
            gridLines: {
              color: "rgb(234, 236, 244)",
              zeroLineColor: "rgb(234, 236, 244)",
              drawBorder: false,
              borderDash: [2],
              zeroLineBorderDash: [2]
            }
          }],
        },
        legend: {
          display: false
        },
        tooltips: {
          titleMarginBottom: 10,
          titleFontColor: '#6e707e',
          titleFontSize: 14,
          backgroundColor: "rgb(255,255,255)",
          bodyFontColor: "#858796",
          borderColor: '#dddfeb',
          borderWidth: 1,
          xPadding: 15,
          yPadding: 15,
          displayColors: false,
          caretPadding: 10,
          callbacks: {
            label: function(tooltipItem, chart) {
              var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
              return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
            }
          }
        },
      }
    });

    return true;
  }

  return false;
}
