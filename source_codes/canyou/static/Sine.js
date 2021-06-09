const myImage = new Image();
myImage.src = url64;

// no flag here
myImage.addEventListener("load", () => {
  const canvas = document.getElementById("canvas6");
  const ctx = canvas.getContext("2d");
  canvas.width = 600;
  canvas.height = 600;

  ctx.drawImage(myImage, 0, 0, canvas.width, canvas.height);
  const pixel = ctx.getImageData(0, 0, canvas.width, canvas.height);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  let particleArray = [];
  const numOfParticles = 3000;

  let mappedImage = [];
  for (let y = 0; y < canvas.height; y++) {
    let row = [];
    for (let x = 0; x < canvas.width; x++) {
      const red = pixel.data[y * 4 * pixel.width + x * 4];
      const green = pixel.data[y * 4 * pixel.width + (x * 4 + 1)];
      const blue = pixel.data[y * 4 * pixel.width + (x * 4 + 2)];
      const brightness = calculateReplativeBright(red, green, blue);
      const cell = [(cellBrightness = brightness)];
      row.push(cell);
    }
    mappedImage.push(row);
  }
  function calculateReplativeBright(red, green, blue) {
    return (
      Math.sqrt(
        red * red * 0.29 + green * green * 0.5 + blue * blue * 0.014
      ) / 85
    );
  }

  class Particles {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = 0;
      this.speen = 0;
      this.velocity = Math.random() * 5.5;
      this.size = Math.random() * 1.5 + 1;
      this.position1 = Math.floor(this.y);
      this.position2 = Math.floor(this.x);
    }

    update() {
      this.position1 = Math.floor(this.y);
      this.position2 = Math.floor(this.x);
      this.speen = mappedImage[this.position1][this.position2][0];
      let movement = 0.5 - this.speen + this.velocity;

      this.y += movement * Math.random();
      if (this.y >= canvas.height) {
        this.y = 0;
        this.x = Math.random() * canvas.width;
      }
    }
    draw() {
      ctx.beginPath();
      ctx.fillStyle = `rgba(226,${Math.random() * 80 + 1},34, ${Math.random()})`;
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  function init() {
    for (let i = 0; i < numOfParticles; i++) {
      particleArray.push(new Particles());
    }
  }

  init();
  function animate() {
    ctx.globalAlpha = 0.05;
    ctx.fillStyle = "rgb(0, 0, 0)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    //ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (let i = 0; i < particleArray.length; i++) {
      particleArray[i].update();
      ctx.globalAlpha = particleArray[i].speen * 0.5;
      particleArray[i].draw();
    }
    requestAnimationFrame(animate);
  }
  animate();
});
