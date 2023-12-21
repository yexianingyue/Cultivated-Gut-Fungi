### Global
library(ComplexHeatmap)
library(dplyr)
library(reshape2)
library(circlize)
library(ggrepel)
library(ggplot2)
library(patchwork)

### Figure 6a
rm(list=ls())
new_vars <- load("fig6.a.RData")

x_min = min(data$CAP1)
x_max = max(data$CAP1)
y_min = min(data$CAP2)
y_max = max(data$CAP2)

p <- ggscatter(data=data, x="CAP1",y="CAP2",color="Group",
               shape="proj", ellipse = F, ellipse.level = 0.6)+
    xlim(x_min, x_max)+
    ylim(y_min, y_max)+
    theme_bw()+
    scale_shape_manual(values=c(0,1,2,3,4))

yplot <-
    data %>%
    ggplot(.,aes(y=CAP2,x=Group, fill=Group))+
    geom_boxplot()+
    theme_bw()+
    geom_signif(comparisons = combn(unique(data$Group),2,list),test='wilcox.test',step_increase = 0.1) + # 用它就注释ylim
    theme(axis.title.y = element_blank(),
          axis.text.x = element_text(angle=90),
          legend.position = "none")

xplot <-
    data %>%
    ggplot(.,aes(x=CAP1,y=Group, fill=Group))+
    geom_boxplot() +
    geom_signif(comparisons =combn(unique(data$Group),2,list),test='wilcox.test',step_increase = 0.1)+# 用它就注释xlim
    theme_bw()+
    theme(axis.title.x = element_blank(),
          legend.position = "none")

fig6a <- xplot+ggplot()+
    p+yplot+
    plot_layout(ncol=2,nrow=2,
                widths=c(4,1),
                heights=c(1,4))

ggsave("fig6a.pdf", fig6a, width=10, height=10)


### Figure 6b
rm(list=ls())
load("./fig6b.RData")
pdf("fig6b.pdf", width=8,height=22)
get_plot(dt,samp,proj_map)$plot
dev.off()
